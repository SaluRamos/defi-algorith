import os

os.system("cls")

class defi_math:

	lp = 100 #liquidez
	total_circulation = 1000 #total de 'tokens' em circulação
	free_circulation = 1000 #'tokens' que estao em circulação e disponiveis
	closed_circulation = 0 #'tokens' que estao em circulação e indisponiveis (nao maos de usuarios)
	total_supply = 1000000 #total de 'tokens'
	total_free_supply = total_supply - total_circulation #total de 'tokens' menos o total que esta em circulaçao

	#retorna preço atual do token em 'usd'
	def UsdPrice():
		if defi_math.free_circulation + defi_math.closed_circulation > defi_math.total_circulation:
			defi_math.total_circulation = (defi_math.free_circulation + defi_math.closed_circulation)
		atual_price = defi_math.lp/defi_math.total_circulation
		return atual_price
	
	#efetua uma compra
	def Buy(amount_in):
		atual_price = defi_math.UsdPrice()
		defi_math.lp += amount_in
		new_price = defi_math.UsdPrice()
		amount_out = amount_in/new_price
		price_impact = new_price/atual_price
		if amount_out > defi_math.free_circulation:
			defi_math.lp -= amount_in
			return f"INSUFFICIENT_OUTPUT_AMOUNT = {amount_out} tokens" #reverte a transação
		if price_impact >= 1.6:
			defi_math.lp -= amount_in
			return f"PRICE IMPACT IS TOO HIGH = {(price_impact*100) - 100}%" #reverte a transação
		defi_math.free_circulation -= amount_out
		defi_math.closed_circulation += amount_out
		return f"{round(amount_out, 2)} usd", f"{(price_impact*100) - 100}%"
	
	#efetua uma venda
	def Sell(amount_in, from_ = "cc"):
		if from_ == "cc": #closed_circulation
			atual_price = defi_math.UsdPrice()
			amount_out = amount_in*atual_price
			defi_math.lp -= amount_out
			new_price = defi_math.UsdPrice()
			price_impact = new_price/atual_price
			defi_math.closed_circulation -= amount_in
			defi_math.free_circulation += amount_in
			return amount_out, f"{(price_impact*100) - 100}%"
		elif from_ == "tfs": #total_free_supply
			atual_price = defi_math.UsdPrice()
			defi_math.total_free_supply -= amount_in
			defi_math.free_circulation += amount_in
			new_price = defi_math.UsdPrice()
			amount_out = amount_in*new_price
			defi_math.lp -= amount_out
			price_impact = new_price/atual_price
			return f"{round(amount_out, 2)} usd", f"{(price_impact*100) - 100}%"

	def TokenInfo():
		print("--------------------")
		print(f"liquidity = {defi_math.lp}")
		print(f"total_supply = {defi_math.total_supply}")
		print(f"total_free_supply = {defi_math.total_free_supply}")
		print(f"total_circulation = {defi_math.total_circulation}")
		print(f"free_circulation = {defi_math.free_circulation}")
		print(f"closed_circulation = {defi_math.closed_circulation}")
		print(f"atual_price = {defi_math.UsdPrice()}")
		print("--------------------")

defi_math.TokenInfo()
print(defi_math.Buy(50))
defi_math.TokenInfo()
print(defi_math.Sell(300, "tfs"))
defi_math.TokenInfo()