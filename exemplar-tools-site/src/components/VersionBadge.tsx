interface Props {
  version: string
  accent: string
}

export default function VersionBadge({ version, accent }: Props) {
  return (
    <span
      className="inline-flex items-center gap-1 font-mono text-xs px-2 py-0.5 rounded border"
      style={{ color: accent, borderColor: accent + '55', background: accent + '11' }}
    >
      v{version}
    </span>
  )
}
