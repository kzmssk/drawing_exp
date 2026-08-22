// backend(/api)への薄い fetch ヘルパ。検証は呼び出し側で zod により行う。

export async function getJson(path: string): Promise<unknown> {
  const res = await fetch(`/api${path}`)
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`)
  }
  return res.json()
}
