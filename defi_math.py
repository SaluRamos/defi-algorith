import os
from eth_account import Account
import secrets
import decimal

class Vars:

    name = ""
    symbol = ""
    decimals = 18
    total_supply = 100000000

    busd_balances = {}
    token_balances = {}
    allowance = {}

    owner_address = "0x0000000000000000000000000000000000000000"
    burn_address = "0x000000000000000000000000000000000000dEaD"
    liquidity_holder_address = "0x9999999999999999999999999999999999999999"

    busd_balances[liquidity_holder_address] = 3
    token_balances[liquidity_holder_address] = 3
    busd_balances[owner_address] = 0
    token_balances[owner_address] = total_supply - token_balances[liquidity_holder_address]

    max_price_impact_on_buy = 38.55
    #max buy of 0,4511
    #se eu comprasse, circulação seria = 2,5489
    #e liquidez = 3 + 0,532265 = 3,532265
    #o preço saltaria de 1 para 1,3857
    #price impact de 38,55%
    max_price_impact_on_sell = -100
    #max sell of 0,5323
    #se eu vendesse, circulação seria = 3,5323
    #e liquidez = 3 - 0,451124 = 2,548876
    #o preço saltaria de 1 para 0,7215
    #price impact de -27.85%

class General:

    def CreateWallet(wallet_busd_balance = 100):
        priv = secrets.token_hex(32)
        private_key = "0x" + priv
        new_wallet_address = General.PVKToAdress(private_key)
        Vars.busd_balances[new_wallet_address] = wallet_busd_balance
        Vars.token_balances[new_wallet_address] = 0
        return {"address":new_wallet_address, "private_key":private_key}

    def PVKToAdress(wallet_pvk):
        return str(Account.from_key(wallet_pvk).address)

    def VerifyWalletAddress(wallet_address):
        wallet_address = wallet_address.lower()
        wallet_address_chars = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "x", "A", "B", "C", "D", "E", "F", "X"]
        for i in wallet_address:
            if i not in wallet_address_chars:
                return False
        return True

class Defi:

    def TokenUsdPrice():
        return Vars.busd_balances[Vars.liquidity_holder_address]/Vars.token_balances[Vars.liquidity_holder_address]

    def BuyInTokens(amount_tokens, from_):
        revert_to = [Vars.token_balances[Vars.liquidity_holder_address], Vars.busd_balances[Vars.liquidity_holder_address], Vars.token_balances[from_], Vars.busd_balances[from_]]
        if amount_tokens >= Vars.token_balances[Vars.liquidity_holder_address]:
            print(f"wallet '{from_}' tryed to buy all (or more) tokens!")
            return
        atual_price = Defi.TokenUsdPrice()
        Vars.token_balances[from_] += amount_tokens
        Vars.token_balances[Vars.liquidity_holder_address] -= amount_tokens
        bought_price = Defi.TokenUsdPrice()
        amount_in = bought_price*amount_tokens
        Vars.busd_balances[from_] -= amount_in
        Vars.busd_balances[Vars.liquidity_holder_address] += amount_in
        new_price = Defi.TokenUsdPrice()
        price_impact = ((new_price/atual_price)-1)*100
        if revert_to[3] < amount_in:
            print(f"wallet '{from_}' tryed to buy '{amount_tokens} tokens' for '{amount_in} busd' but dont have enough busd")
            Defi.Revert(revert_to, from_)
            return
        if price_impact >= Vars.max_price_impact_on_buy:
            print(f"wallet '{from_}' tryed to buy '{amount_tokens} tokens' but had a price impact too high of '{round(price_impact, 2)}%'")
            Defi.Revert(revert_to, from_)
            return
        print(f"wallet '{from_}' bought '{amount_tokens} tokens' for '{amount_in} busd', with a price of '{atual_price} busd' that changed to '{new_price} busd', the price impact was '{round(price_impact, 2)}%'")

    def SellInTokens(amount_tokens, from_):
        revert_to = [Vars.token_balances[Vars.liquidity_holder_address], Vars.busd_balances[Vars.liquidity_holder_address], Vars.token_balances[from_], Vars.busd_balances[from_]]
        atual_price = Defi.TokenUsdPrice()
        Vars.token_balances[from_] -= amount_tokens
        Vars.token_balances[Vars.liquidity_holder_address] += amount_tokens
        sold_price = Defi.TokenUsdPrice()
        amount_out = sold_price*amount_tokens
        Vars.busd_balances[from_] += amount_out
        Vars.busd_balances[Vars.liquidity_holder_address] -= amount_out
        new_price = Defi.TokenUsdPrice()
        price_impact = ((new_price/atual_price)-1)*100
        if revert_to[2] < amount_tokens:
            print(f"wallet '{from_}' tryed to sell '{amount_tokens} tokens' for '{amount_out} busd' but dont have enough tokens")
            Defi.Revert(revert_to, from_)
            return
        if price_impact <= Vars.max_price_impact_on_sell:
            print(f"wallet '{from_}' tryed to sell '{amount_tokens} tokens' but had a price impact too high of '{round(price_impact, 2)}%'")
            Defi.Revert(revert_to, from_)
            return
        print(f"wallet '{from_}' sold '{amount_tokens} tokens' for '{amount_out} busd', with a price of '{atual_price} busd' that changed to '{new_price} busd', the price impact was '{round(price_impact, 2)}%'")

    def BuyInBusd(amount_busd, from_):
        revert_to = [Vars.token_balances[Vars.liquidity_holder_address], Vars.busd_balances[Vars.liquidity_holder_address], Vars.token_balances[from_], Vars.busd_balances[from_]]
        atual_price = Defi.TokenUsdPrice()
        Vars.busd_balances[from_] -= amount_busd
        Vars.busd_balances[Vars.liquidity_holder_address] += amount_busd
        bought_price = Defi.TokenUsdPrice()
        amount_out = amount_busd/bought_price
        if amount_out >= Vars.token_balances[Vars.liquidity_holder_address]:
            print(f"wallet '{from_}' tryed to buy all (or more) tokens!")
            Defi.Revert(revert_to, from_)
            return
        Vars.token_balances[from_] += amount_out
        Vars.token_balances[Vars.liquidity_holder_address] -= amount_out
        new_price = Defi.TokenUsdPrice()
        price_impact = ((new_price/atual_price)-1)*100
        if revert_to[3] < amount_busd:
            print(f"wallet '{from_}' tryed to buy '{amount_out} tokens' for '{amount_busd} busd' but dont have enough busd")
            Defi.Revert(revert_to, from_)
            return
        if price_impact >= Vars.max_price_impact_on_buy:
            print(f"wallet '{from_}' tryed to buy '{amount_out} tokens' but had a price impact too high of '{round(price_impact, 2)}%'")
            Defi.Revert(revert_to, from_)
            return
        print(f"wallet '{from_}' bought '{amount_out} tokens' for '{amount_busd} busd', with a price of '{atual_price} busd' that changed to '{new_price} busd', the price impact was '{round(price_impact, 2)}%'")

    def SellInBusd(amount_busd, from_):
        revert_to = [Vars.token_balances[Vars.liquidity_holder_address], Vars.busd_balances[Vars.liquidity_holder_address], Vars.token_balances[from_], Vars.busd_balances[from_]]
        atual_price = Defi.TokenUsdPrice()
        Vars.busd_balances[from_] += amount_busd
        Vars.busd_balances[Vars.liquidity_holder_address] -= amount_busd
        sold_price = Defi.TokenUsdPrice()
        amount_out = amount_busd/sold_price
        Vars.token_balances[from_] -= amount_out
        Vars.token_balances[Vars.liquidity_holder_address] += amount_out
        new_price = Defi.TokenUsdPrice()
        price_impact = ((new_price/atual_price)-1)*100
        if revert_to[2] < amount_out:
            print(f"wallet '{from_}' tryed to sell '{amount_out} tokens' for '{amount_busd} busd' but dont have enough tokens")
            Defi.Revert(revert_to, from_)
            return
        if price_impact <= Vars.max_price_impact_on_sell:
            print(f"wallet '{from_}' tryed to sell '{amount_out} tokens' but had a price impact too high of '{round(price_impact, 2)}%'")
            Defi.Revert(revert_to, from_)
            return
        print(f"wallet '{from_}' sold '{amount_out} tokens' for '{amount_busd} busd', with a price of '{atual_price} busd' that changed to '{new_price} busd', the price impact was '{round(price_impact, 2)}%'")

    def Print_Statistics():
        print("----------------------------------------------------")
        print(f"BUSD BALANCES:\n{Vars.busd_balances}")
        print(f"TOKEN BALANCES:\n{Vars.token_balances}")
        print(f"TOKEN PRICE: {Defi.TokenUsdPrice()}")
        print("----------------------------------------------------")

    def Revert(revert_to, from_):
        Vars.token_balances[Vars.liquidity_holder_address] = revert_to[0]
        Vars.busd_balances[Vars.liquidity_holder_address] = revert_to[1]
        Vars.token_balances[from_] = revert_to[2]
        Vars.busd_balances[from_] = revert_to[3]
        print("TRANSAÇÃO REVERTIDA")
    
os.system("cls")
new_wallet = General.CreateWallet(10000)["address"]
Defi.BuyInTokens(0.1, new_wallet)
Defi.Print_Statistics()
Defi.SellInTokens(0.1, new_wallet)
Defi.Print_Statistics()
#Defi.SellInTokens(Vars.token_balances[Vars.owner_address], Vars.owner_address)
# Defi.Print_Statistics()