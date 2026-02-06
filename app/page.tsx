export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-4xl text-center">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          TikTik Smart Order System
        </h1>
        <p className="text-lg text-muted-foreground mb-8">
          Welcome to the TikTik Smart Order System - Your intelligent solution for event ticketing, concerts, and sports venues.
        </p>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 text-left">
          <div className="rounded-lg border bg-card p-6">
            <h2 className="font-semibold mb-2">Event Management</h2>
            <p className="text-sm text-muted-foreground">
              Manage concerts, sports events, and more
            </p>
          </div>
          <div className="rounded-lg border bg-card p-6">
            <h2 className="font-semibold mb-2">Smart Ordering</h2>
            <p className="text-sm text-muted-foreground">
              Intelligent ticket and seat selection system
            </p>
          </div>
          <div className="rounded-lg border bg-card p-6">
            <h2 className="font-semibold mb-2">Stadium Maps</h2>
            <p className="text-sm text-muted-foreground">
              Interactive stadium and venue layouts
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
