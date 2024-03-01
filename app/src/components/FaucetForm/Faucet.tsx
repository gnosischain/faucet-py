/* eslint-disable */
import { useState, ChangeEvent } from "react"
import Select, { ActionMeta, StylesConfig } from 'react-select'
import "./Faucet.css"


interface Option {
  value: string,
  token: string,
  maximumAmount: string
}

const customStyles: StylesConfig<Option, false> = {
  control: (provided) => ({
    ...provided,
    height: "56px"
  })
}

interface IToken {
  address: string
  name: string
  maximumAmount: string | number
}

interface IFaucetProps {
  enabledTokens: IToken[]
}

const formatOptionLabel = ({ token, maximumAmount }: Option) => {
  return (
    <div>
      <strong>{token}</strong> {maximumAmount}
    </div>
  )
}

function Faucet({ enabledTokens }: IFaucetProps): JSX.Element {
  const [address, setAddress] = useState("")

  const handleChangeAddress = (event: ChangeEvent<HTMLInputElement>) => {
    setAddress(event.target.value);
  }

  const handleChangeToken = (option: Option | null, actionMeta: ActionMeta<Option>) => {
    console.log('Selected option:', option);
 }

  const options: Option[] = enabledTokens.map((item) => {
    return {
      value: item.address,
      token: item.name,
      maximumAmount: `${item.maximumAmount} day`
    }
  })
  
  return (
    <div className="faucet-container">
      <p>Paste your account address in the field below and choose if you want to receive either a portion of the native token or any of the enabled ERC20 tokens.</p>
      <div className="flex-row">
        <label htmlFor="address">Wallet address:</label>
        <input
          type="text"
          value={address}
          placeholder="0x123..."
          onChange={handleChangeAddress}
          id="address"
        />
      </div>
      <div className="flex-row">
        <label htmlFor="token">Choose token:</label>
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
  )
}

export default Faucet
