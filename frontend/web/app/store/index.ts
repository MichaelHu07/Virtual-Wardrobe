import { create } from 'zustand'

interface UserState {
  userId: string | null
  setUserId: (id: string) => void
}

interface WardrobeState {
  garments: any[]
  setGarments: (items: any[]) => void
  addGarment: (item: any) => void
}

export const useUserStore = create<UserState>((set) => ({
  userId: null,
  setUserId: (id) => set({ userId: id }),
}))

export const useWardrobeStore = create<WardrobeState>((set) => ({
  garments: [],
  setGarments: (items) => set({ garments: items }),
  addGarment: (item) => set((state) => ({ garments: [...state.garments, item] })),
}))

