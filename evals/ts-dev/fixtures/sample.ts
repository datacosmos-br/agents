export async function loadName(response: Response): Promise<string> {
  const payload: any = await response.json();
  return payload.user.name;
}
