import { useState, useRef, ChangeEvent, FormEvent, useEffect, Dispatch, SetStateAction } from "react"
import "./Faucet.css"
import { toast } from "react-toastify"
import axios from "axios"
import Captcha from "../Captcha/Captcha"
import TokenSelect, { Token } from "../TokenSelect/TokenSelect"
import HCaptcha from "@hcaptcha/react-hcaptcha"
import { formatLimit } from "../../utils"

interface FaucetProps {
  enabledTokens: Token[],
  chainId: number,
  setLoading: Dispatch<SetStateAction<boolean>>,
  csrfToken: string,
  requestId: string,
  timestamp: number
}

const blockscanner:{ [key: string]: string }= {
  100: "https://gnosisscan.io/tx/",
  10200: "https://gnosis-chiado.blockscout.com/tx/"
}

function Faucet({ enabledTokens, chainId, setLoading, csrfToken, requestId, timestamp }: FaucetProps): JSX.Element {
  const [walletAddress, setWalletAddress] = useState<string>("")
  const [token, setToken] = useState<Token | null>(null)
  const [captchaToken, setCaptchaToken] = useState<string | null>(null)
  const [txHash, setTxHash] = useState<string | null>(null)
  const [windowWidth, setWindowWidth] = useState<number>(window.innerWidth)
  const [requestOngoing, setRequestOngoing] = useState(false)

  const captchaRef = useRef<HCaptcha>(null)

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener("resize", handleResize)

    const searchParams = new URLSearchParams(window.location.search)
    const addressFromURL = searchParams.get("address")
    if (addressFromURL) {
      setWalletAddress(addressFromURL)
    }

    return () => window.removeEventListener("resize", handleResize)
  }, [])


  useEffect(() => {
    if (enabledTokens.length === 1) {
      setToken({
        address: enabledTokens[0].address,
        name: enabledTokens[0].name,
        maximumAmount: Number(enabledTokens[0].maximumAmount),
        rateLimitDays: enabledTokens[0].rateLimitDays
      })
    } else {
      const defaultToken = enabledTokens.find(token => token.address === "0x0000000000000000000000000000000000000000")
      if (defaultToken !== undefined) {
        setToken({
          address: defaultToken.address,
          name: defaultToken.name,
          maximumAmount: Number(defaultToken.maximumAmount),
          rateLimitDays: defaultToken.rateLimitDays
        })
      }
    }
  }, [enabledTokens.length])

  function formatErrors(errors: string[]) {
    return (
      <div>
        { errors.map((item, index) => <div key={index}>{item}</div>)}
      </div>
    )
  }

  const handleChangeAddress = (event: ChangeEvent<HTMLInputElement>) => {
    setWalletAddress(event.target.value)
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
 
    if (walletAddress.length <= 0) {
      toast.error("Please provide a wallet address.")
      return
    }

    const apiURL = `${process.env.REACT_APP_FAUCET_API_URL}/ask`

    if (token) {
      setLoading(true)
      setRequestOngoing(true)
      try {
        const requestData = {
          recipient: walletAddress,
          captcha: captchaToken,
          tokenAddress: token.address,
          chainId: chainId,
          amount: token.maximumAmount,
          requestId: requestId,
          timestamp: timestamp
        }

        const headers = {
          'X-CSRFToken': csrfToken
        }

        setTimeout(function() {
          axios
          .post(apiURL, requestData, {
            headers: headers
          })
          .then((response) => {
            setWalletAddress("")

            if (enabledTokens.length > 1 ) {
              setToken(null)
            }
   
            // Reset captcha
            setCaptchaToken("")
            captchaRef.current?.resetCaptcha()

            setLoading(false)
            setRequestOngoing(false)

            toast.success("Token sent to your wallet address")
            setTxHash(`${response.data.transactionHash}`)
          })
          .catch((error) => {
            toast.error(formatErrors(error.response.data.errors))
            setLoading(false)
            setRequestOngoing(false)
          })
        }, 10000) // 10 seconds delay
      } catch (error) {
        if (error instanceof Error) {
          toast.error(error.message)
        }
        setLoading(false)
        setRequestOngoing(false)
      }
    }
  }
  
  return (
    <form onSubmit={handleSubmit} className="faucet-container">
      <p>Paste your account address in the field below and choose if you want to receive either a portion of the native token or any of the enabled ERC20 tokens.</p>
      <div className="flex-row">
        <label htmlFor="address">Wallet address:</label>
        <div className="input-field">
          <input
            type="text"
            value={walletAddress}
            placeholder="0x123..."
            onChange={handleChangeAddress}
            id="address"
            required
          />
        </div>
      </div>
      <div className="flex-row">
        {(enabledTokens.length === 1 && token) ?
          <>
            <label htmlFor="token">Token:</label>
            <div className="input-field token-info">
              <strong>{token.name}</strong> {token.maximumAmount} / {formatLimit(token.rateLimitDays)}
            </div>
          </> :
          <>
            <label htmlFor="token">Choose token:</label>
            <div className="input-field">
              <TokenSelect
                enabledTokens={enabledTokens}
                token={token}
                setToken={setToken}
                windowWidth={windowWidth}
              />
            </div>
          </>
        }
      </div>
      <div className="flex-row flex-row-captcha">
        <Captcha
          setCaptchaToken={setCaptchaToken}
          windowWidth={windowWidth}
          captchaRef={captchaRef}
        />
      </div>
      <button type="submit" disabled={!captchaToken || requestOngoing}>
        {requestOngoing && <span>We are claiming your tokens... hold on</span> || <span>Claim</span>}
      </button>
      {txHash &&
        <div className="flex-row success">
          <div>Token sent to your wallet address. Hash: </div> 
          <div>
            <a
              target="_blank"
              rel="noreferrer"
              href={`${blockscanner[String(chainId)]}${txHash}`}
            >{txHash}</a>
          </div>
        </div>
      }
    </form>
  )
}

export default Faucet
