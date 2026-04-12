import { AlertCircle } from 'lucide-react'

export default function ErrorMessage({ message }: { message?: string }) {
  return (
    <div className="flex items-center gap-3 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
      <AlertCircle size={18} className="shrink-0" />
      <span>{message ?? 'Something went wrong. Please try again.'}</span>
    </div>
  )
}
