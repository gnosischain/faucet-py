/* eslint-disable */
import { useState, ChangeEvent, FormEvent, useEffect } from "react"
import "./Faucet.css"
import { toast } from "react-toastify"
import axios from "axios"
import Captcha from "../Captcha/Captcha"
import TokenSelect, { Token } from "../TokenSelect/TokenSelect"

interface FaucetProps {
  enabledTokens: Token[],
  chainId: string
}

function Faucet({ enabledTokens, chainId }: FaucetProps): JSX.Element {
  const [walletAddress, setWalletAddress] = useState("")
  const [token, setToken] = useState<Token | null>(null)

  const [captchaToken, setCaptchaToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const [txHash, setTxHash] = useState<string | null>(null)

  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => setWindowWidth(window.innerWidth)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

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

    setTxHash("0xb241d0f92fff78f01f9f3410593294191be6dab323c3844f668d466dea835801")
    toast.success(`Token sent to your wallet address. Hash: 0xlkdjflskjfl`)

    // if (token) {
    //   try {
    //     setLoading(true)
    //     const req = {
    //       recipient: walletAddress,
    //       captcha: captchaToken,
    //       tokenAddress: token.address,
    //       chainId: chainId,
    //       amount: token.maximumAmount
    //     }

    //     axios
    //       .post(apiURL, req)
    //       .then((response) => {
    //         setLoading(false)
    //         setWalletAddress("")
    //         // Reset captcha
    //         // setCaptchaVerified(true)
    //         // captchaRef.current?.resetCaptcha()

    //         setToken(null)

    //         toast.success(`Token sent to your wallet address. Hash: ${response.data.transactionHash}`)
    //         setTxInfo(`Token sent to your wallet address. Hash: ${response.data.transactionHash}`)
    //       })
    //       .catch((error) => {
    //         setLoading(false)
    //         console.log(error)
    //         // toast.error(formatErrors(error.response.data.errors))
    //       })
    //   } catch (error) {
    //     setLoading(false)
    //     if (error instanceof Error) {
    //       toast.error(error.message)
    //     }
    //   }
    // }
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
        <label htmlFor="token">Choose token:</label>
        <div className="input-field">
          <TokenSelect
            enabledTokens={enabledTokens}
            token={token}
            setToken={setToken}
            windowWidth={windowWidth}
          />
        </div>
      </div>
      <div className="flex-row flex-row-captcha">
        <Captcha setCaptchaToken={setCaptchaToken} windowWidth={windowWidth}/>
      </div>
      <button type="submit">
        Claim
      </button>
      {txHash &&
        <div className="flex-row success">
          <div>Token sent to your wallet address. Hash: </div> 
          <div>
            {chainId === "100"
              ? <a target="_blank" href={`https://gnosisscan.io/tx/${txHash}`}>{txHash}</a>
              : txHash
            }
          </div>
        </div>
      }
    </form>
  )
}

export default Faucet
