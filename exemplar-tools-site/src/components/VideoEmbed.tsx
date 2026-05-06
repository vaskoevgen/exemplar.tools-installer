interface Props {
  url: string
  title: string
}

export default function VideoEmbed({ url, title }: Props) {
  return (
    <div className="my-8 rounded-xl overflow-hidden border border-[#1e1e2e] aspect-video">
      <iframe
        src={url}
        title={title}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
        className="w-full h-full"
      />
    </div>
  )
}
