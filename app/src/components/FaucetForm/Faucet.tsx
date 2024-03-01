/* eslint-disable */
import { useState, ChangeEvent, FormEvent, useEffect } from "react"
import Select, { ActionMeta, StylesConfig } from "react-select"
import "./Faucet.css"
import { toast } from "react-toastify"
import axios from "axios"
import Captcha from "../Captcha/Captcha"

interface Option {
  value: string,
  token: string,
  maximumAmount: string
}

const customStyles: StylesConfig<Option, false> = {
  control: (provided) => ({
    ...provided,
    height: "56px",
    width: window.innerWidth > 500 ? "303px" : "auto",
    border: "none"
  })
}

interface IToken {
  address: string
  name: string
  maximumAmount: string | number
}

interface IFaucetProps {
  enabledTokens: IToken[],
  chainId: string
}

const formatOptionLabel = ({ token, maximumAmount }: Option) => {
  return (
    <div>
      <strong>{token}</strong> {maximumAmount}
    </div>
  )
}

function Faucet({ enabledTokens, chainId }: IFaucetProps): JSX.Element {
  const [walletAddress, setWalletAddress] = useState("")
  const [tokenAddress, setTokenAddress] = useState("")
  const [tokenAmount, setTokenAmount] = useState(0)
  const [captchaToken, setCaptchaToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const handleChangeAddress = (event: ChangeEvent<HTMLInputElement>) => {
    setWalletAddress(event.target.value);
  }

  const handleChangeToken = (option: Option | null, actionMeta: ActionMeta<Option>) => {
    console.log('Selected option:', option)

    if (option) {
      for (let idx in enabledTokens) {
        if (enabledTokens[idx].address.toLowerCase() == option.value.toLowerCase()) {
          setTokenAmount(Number(enabledTokens[idx].maximumAmount))
          break
        }
      }
    }
    setTokenAddress(option?.value || "")
  }

  const options: Option[] = enabledTokens.map((item) => {
    return {
      value: item.address,
      token: item.name,
      maximumAmount: `${item.maximumAmount} day`
    }
  })

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
 
    if (walletAddress.length <= 0) {
      toast.error("Please provide a wallet address.")
      return;
    }

    const apiURL = `${process.env.REACT_APP_FAUCET_API_URL}/ask`

    try {
      setLoading(true);
      const req = {
        recipient: walletAddress,
        captcha: captchaToken,
        tokenAddress: tokenAddress,
        chainId: chainId,
        amount: tokenAmount,
      };

      axios
        .post(apiURL, req)
        .then((response) => {
          setLoading(false);
          setWalletAddress("");
          // Reset captcha
          // setCaptchaVerified(true)
          // captchaRef.current?.resetCaptcha()

          toast.success(`Tokens sent to your wallet address. Hash: ${response.data.transactionHash}`)
        })
        .catch((error) => {
          setLoading(false)
          console.log(error)
          // toast.error(formatErrors(error.response.data.errors));
        })
    } catch (error) {
      setLoading(false)
      if (error instanceof Error) {
        toast.error(error.message)
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
          />
        </div>
      </div>
      <div className="flex-row">
        <label htmlFor="token">Choose token:</label>
        <div className="input-field">
          <Select
            styles={customStyles}
            className="token-select"
            options={options}
            formatOptionLabel={formatOptionLabel}
            onChange={handleChangeToken}
            id="address"
          />
        </div>
      </div>
      <div className="flex-row flex-row-captcha">
        <Captcha setCaptchaToken={setCaptchaToken} />
      </div>
      <button type="submit">
        Claim
      </button>
    </form>
  )
}

export default Faucet
