export default function LoadingSpinner({ message = 'Loading…' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3">
      <div className="w-8 h-8 border-2 border-gray-700 border-t-blue-500 rounded-full animate-spin" />
      <p className="text-sm text-gray-500">{message}</p>
    </div>
  )
}
