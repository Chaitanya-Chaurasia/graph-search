export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-center px-6 py-16">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Maps Clone
        </h1>
        <p className="mt-2 text-zinc-600 dark:text-zinc-400">
          Shortest routes + ETA. Connect to the backend to load the map.
        </p>
      </main>
    </div>
  );
}
