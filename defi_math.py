import os
import decimal

os.system("cls")

class defi_math:
	
	lp = decimal.Decimal("100") #liquidez
	total_circulation = decimal.Decimal("1000") #total de 'tokens' em circulação
	free_circulation = total_circulation #'tokens' que estao em circulação e disponiveis
	closed_circulation = decimal.Decimal("0") #'tokens' que estao em circulação e indisponiveis (nao maos de usuarios)
	total_supply = decimal.Decimal("1000000") #total de 'tokens'
	total_free_supply = total_supply - total_circulation #total de 'tokens' menos o total que esta em circulaçao
	max_buy_price_impact = 1.5

	#retorna preço atual do token em 'usd'
	def UsdPrice():
		if defi_math.free_circulation + defi_math.closed_circulation > defi_math.total_circulation:
			defi_math.total_circulation = (defi_math.free_circulation + defi_math.closed_circulation)
		atual_price = defi_math.lp/defi_math.free_circulation
		return atual_price
	
	#efetua uma compra
	def Buy(amount_in):
		atual_price = defi_math.UsdPrice()
		defi_math.lp += amount_in
		new_price = defi_math.UsdPrice()
		amount_out = amount_in/new_price
		price_impact = new_price/atual_price
		if amount_out >= defi_math.free_circulation:
			defi_math.lp -= amount_in
			return f"INSUFFICIENT_OUTPUT_AMOUNT = {amount_out} tokens" #reverte a transação
		if price_impact > defi_math.max_buy_price_impact:
			defi_math.lp -= amount_in
			return f"PRICE IMPACT IS TOO HIGH = {(price_impact*100) - 100}%" #reverte a transação
		defi_math.free_circulation -= amount_out
		defi_math.closed_circulation += amount_out
		return f"{round(amount_out, 2)} tokens", f"{(price_impact*100) - 100}%"

	def BuyPriceImpact(amount_in):
		atual_price = defi_math.UsdPrice()
		fake_lp = defi_math.lp
		fake_lp += amount_in
		new_price = fake_lp/defi_math.total_circulation
		amount_out = amount_in/new_price
		price_impact = new_price/atual_price
		return {"price_impact":price_impact, "amount_out":amount_out}

	#efetua uma compra
	def MaxBuy():
		max_amount_in = 0
		total_tests = 0
		for i in range(100000):
			new_test = defi_math.BuyPriceImpact(decimal.Decimal((i + 1)*0.01))
			if new_test["amount_out"] > defi_math.free_circulation:
				max_amount_in = decimal.Decimal((i)*0.01)
				total_tests = i
				break
			if new_test["price_impact"] < defi_math.max_buy_price_impact and new_test["price_impact"] > 0.999*defi_math.max_buy_price_impact:
				max_amount_in = decimal.Decimal((i + 1)*0.01)
				total_tests = i + 1
				break
		print(f"max_buy = {max_amount_in} usd")
		print(f"total_tests = {total_tests}")
		return defi_math.Buy(max_amount_in)
	
	#efetua uma venda
	def Sell(amount_in, from_ = "cc"):
		if from_ == "cc": #closed_circulation
			if amount_in > defi_math.closed_circulation:
				return "CANT BE A CC TRANSACTION! MAYBE IT IS A TFS?"
			atual_price = defi_math.UsdPrice()
			amount_out = amount_in*atual_price
			defi_math.lp -= amount_out
			new_price = defi_math.UsdPrice()
			price_impact = new_price/atual_price
			defi_math.closed_circulation -= amount_in
			defi_math.free_circulation += amount_in
			return amount_out, f"{(price_impact*100) - 100}%"
		elif from_ == "tfs": #total_free_supply
			#LEMBRETE, NÃO POSSUO CONFIRMAÇÕES QUE TFS POSSUI O ALGORITMO EXATO, MAS É MUITO PRÓXIMO!
			atual_price = defi_math.UsdPrice()
			defi_math.total_free_supply -= amount_in
			defi_math.free_circulation += amount_in
			new_price = defi_math.UsdPrice()
			amount_out = amount_in*new_price
			defi_math.lp -= amount_out
			price_impact = new_price/atual_price
			return f"{round(amount_out, 2)} usd", f"{(price_impact*100) - 100}%"

	#mostra as informações atuais do token
	def TokenInfo():
		print("--------------------")
		print(f"liquidity = {defi_math.lp} usd")
		print(f"total_supply = {defi_math.total_supply} tokens")
		print(f"total_free_supply = {defi_math.total_free_supply} tokens")
		print(f"total_circulation = {defi_math.total_circulation} tokens")
		print(f"free_circulation = {defi_math.free_circulation} tokens")
		print(f"closed_circulation = {defi_math.closed_circulation} tokens")
		print(f"atual_price = {defi_math.UsdPrice()} usd")
		print("--------------------")

	#efetua um hugpull com todos os tokens que não estao em circulação
	def HugPull():
		return defi_math.Sell(defi_math.total_free_supply, "tfs")

defi_math.TokenInfo()
print(defi_math.Buy(10))
defi_math.TokenInfo()
print(defi_math.Sell(defi_math.closed_circulation))
defi_math.TokenInfo()