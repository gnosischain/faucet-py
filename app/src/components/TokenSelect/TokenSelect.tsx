import { Dispatch, SetStateAction } from "react"
import Select, { StylesConfig } from "react-select"

export interface Token {
  address: string
  name: string
  maximumAmount: number
}

interface TokenSelectProps {
  enabledTokens: Token[],
  token: Token | null,
  setToken: Dispatch<SetStateAction<Token | null>>
  windowWidth: number
}

const formatOptionLabel = ({ name, maximumAmount }: Token) => {
  return (
    <div>
      <strong>{name}</strong> {maximumAmount} / day
    </div>
  )
}

const getOptionValue = (option: Token) => option.address

function TokenSelect ({ enabledTokens, token, setToken, windowWidth }: TokenSelectProps): JSX.Element {

  const handleChangeToken = (option: Token | null) => {
    if (option) {
      for (const idx in enabledTokens) {
        if (enabledTokens[idx].address.toLowerCase() == option.address.toLowerCase()) {
          setToken({
            address: option.address,
            name: option.name,
            maximumAmount: Number(enabledTokens[idx].maximumAmount)
          })
          break
        }
      }
    } else {
      setToken(null)
    }
  }

  const customStyles: StylesConfig<Token, false> = {
    control: (provided) => ({
      ...provided,
      height: "56px",
      width: windowWidth > 520 ? "303px" : "auto",
      border: "none"
    })
  }

  return (
    <Select
      styles={customStyles}
      className="token-select"
      options={enabledTokens}
      formatOptionLabel={formatOptionLabel}
      getOptionValue={getOptionValue}
      onChange={handleChangeToken}
      id="token"
      value={token}
      required
    />
  )
}

export default TokenSelect
