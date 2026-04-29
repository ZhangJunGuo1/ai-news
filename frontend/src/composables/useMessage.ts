import { getCurrentInstance } from 'vue'

export function useMessage() {
  const { proxy } = getCurrentInstance()!
  return (proxy as any).$message
}
