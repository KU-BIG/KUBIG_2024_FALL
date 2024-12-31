import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { ChatRoom } from "@prisma/client";

interface ChatroomState {
    chatrooms: ChatRoom[];
    fetchChatrooms: () => Promise<void>;
    createChatroom: (router: any) => Promise<void>;
    deleteChatroom: (id: string, router: any) => Promise<void>;
    renameChatroom: (id: string, newName: string) => Promise<void>;
}

export const useChatroomStore = create<ChatroomState>()(
    persist(
        (set) => ({
            chatrooms: [],

            // ✅ 채팅방 목록 불러오기
            fetchChatrooms: async () => {
                const token = localStorage.getItem("token");
                if (!token) {
                    set({ chatrooms: [] });
                    return;
                }

                try {
                    const response = await fetch("/api/chat", {
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    if (!response.ok) throw new Error("Failed to fetch chatrooms");

                    const data = await response.json();
                    set({ chatrooms: data });
                } catch (error) {
                    console.error("Error fetching chatrooms:", error);
                }
            },

            // ✅ 채팅방 생성 및 이동
            createChatroom: async (router) => {
                const token = localStorage.getItem("token");

                if (!token) {
                    const guestChatroom: ChatRoom = {
                        id: `guest-${Date.now()}`,
                        name: `Guest - ${Date.now()}`,
                        createdAt: new Date(),
                        updatedAt: new Date(),
                        isNameUpdated: true,
                        userId: "guest",
                    };

                    set((state) => ({
                        chatrooms: [...state.chatrooms, guestChatroom],
                    }));
                    router.push(`/chat/${guestChatroom.id}`); // 게스트 채팅방 이동
                    return;
                }

                try {
                    const response = await fetch("/api/chat", {
                        method: "POST",
                        headers: {
                            Authorization: `Bearer ${token}`,
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ name: "New Chat Room" }),
                    });

                    if (!response.ok) throw new Error("Failed to create chatroom");

                    const newChatroom = await response.json();
                    set((state) => ({
                        chatrooms: [...state.chatrooms, newChatroom],
                    }));

                    router.push(`/chat/${newChatroom.id}`); // 새 채팅방 이동
                } catch (error) {
                    console.error("Error creating chatroom:", error);
                }
            },

            // ✅ 채팅방 삭제 및 메인 페이지로 이동
            deleteChatroom: async (id: string, router) => {
                const token = localStorage.getItem("token");
                if (!token) return;

                try {
                    await fetch(`/api/chat/${id}`, {
                        method: "DELETE",
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    set((state) => ({
                        chatrooms: state.chatrooms.filter((chatroom) => chatroom.id !== id),
                    }));

                    router.push("/"); // 삭제 후 메인 페이지 이동
                } catch (error) {
                    console.error("Error deleting chatroom:", error);
                }
            },

            // ✅ 채팅방 이름 변경
            renameChatroom: async (id: string, newName: string) => {
                const token = localStorage.getItem("token");
                if (!token) return;

                try {
                    const response = await fetch(`/api/chat/${id}`, {
                        method: "PATCH",
                        headers: {
                            Authorization: `Bearer ${token}`,
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ name: newName }),
                    });

                    if (!response.ok) throw new Error("Failed to rename chatroom");

                    const updatedChatroom = await response.json();

                    set((state) => ({
                        chatrooms: state.chatrooms.map((chatroom) =>
                            chatroom.id === id ? updatedChatroom : chatroom
                        ),
                    }));
                } catch (error) {
                    console.error("Error renaming chatroom:", error);
                }
            },
        }),
        {
            name: "chatroom-storage",
            storage: createJSONStorage(() => localStorage),
        }
    )
);
