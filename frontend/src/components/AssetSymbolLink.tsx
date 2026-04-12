interface AssetSymbolLinkProps {
  symbol: string | null | undefined
  className?: string
}

export default function AssetSymbolLink({ symbol, className }: AssetSymbolLinkProps) {
  if (!symbol) return <span className={className}>—</span>

  return (
    <a
      href={`https://www.perplexity.ai/finance/${symbol}`}
      target="_blank"
      rel="noopener noreferrer"
      title="Open in Perplexity Finance"
      className={`hover:underline hover:text-blue-300 transition-colors ${className ?? ''}`}
    >
      {symbol}
    </a>
  )
}
