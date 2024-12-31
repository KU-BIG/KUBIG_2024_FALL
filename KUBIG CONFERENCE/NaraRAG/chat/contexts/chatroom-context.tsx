"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { ChatRoom } from "@prisma/client";
import { useRouter } from "next/navigation";

// Context 타입 정의
interface ChatroomContextType {
    chatrooms: ChatRoom[];
    createChatroom: () => Promise<void>;
    deleteChatroom: (id: string) => Promise<void>;
    renameChatroom: (id: string, newName: string) => Promise<void>;
}

// Context 생성
const ChatroomContext = createContext<ChatroomContextType | undefined>(
    undefined
);

// Custom Hook
export const useChatroom = () => {
    const context = useContext(ChatroomContext);
    if (!context) {
        throw new Error("useChatroom must be used within a ChatroomProvider");
    }
    return context;
};

// Provider 컴포넌트
export const ChatroomProvider: React.FC<{ children: React.ReactNode }> = ({
    children,
}) => {
    const [chatrooms, setChatrooms] = useState<ChatRoom[]>([]);
    const router = useRouter();

    const fetchWithAuth = async (
        url: string,
        options: RequestInit = {}
    ): Promise<Response> => {
        const token = localStorage.getItem("token");
        if (!token) {
            await new Promise((resolve) => setTimeout(resolve, 500)); // 0.5초 대기

            const retryToken = localStorage.getItem("token");
            if (!retryToken) {
                throw new Error("로그인 정보가 없습니다. 다시 로그인해주세요.");
            }
        }
        return fetch(url, {
            ...options,
            headers: {
                ...options.headers,
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        });
    };

    const fetchChatrooms = async () => {
        try {
            const response = await fetchWithAuth("/api/chat");
            if (!response.ok) throw new Error("Failed to fetch chatrooms");
            const data = await response.json();
            setChatrooms(data);
        } catch (error) {
            console.error("Failed to fetch chatrooms:", error);
        }
    };

    const createChatroom = async () => {
        try {
            const token = localStorage.getItem("token");
            if (!token) {
                const guestChatroom: ChatRoom = {
                    id: `guest`,
                    name: `Guest - ${Date.now()}`,
                    createdAt: new Date(),
                    updatedAt: new Date(),
                    isNameUpdated: true,
                    userId: "guest",
                };
                setChatrooms((prev) => [...prev, guestChatroom]);
                router.push(`/chat/${guestChatroom.id}`);
                return;
            }

            const response = await fetchWithAuth("/api/chat", {
                method: "POST",
                body: JSON.stringify({ name: "New Chat Room" }),
            });
            if (!response.ok) throw new Error("Failed to create chatroom");
            const newChatroom: ChatRoom = await response.json();
            setChatrooms((prev) => [...prev, newChatroom]);
            router.push(`/chat/${newChatroom.id}`);
        } catch (error) {
            console.error("Error creating chatroom:", error);
            alert("채팅방을 생성할 수 없습니다. 다시 시도해주세요.");
        }
    };

    const deleteChatroom = async (id: string) => {
        try {
            await fetchWithAuth(`/api/chat/${id}`, { method: "DELETE" });
            setChatrooms((prev) =>
                prev.filter((chatroom) => chatroom.id !== id)
            );
            router.push("/");
        } catch (error) {
            console.error("Error deleting chatroom:", error);
        }
    };

    const renameChatroom = async (id: string, newName: string) => {
        try {
            const response = await fetchWithAuth(`/api/chat/${id}`, {
                method: "PATCH",
                body: JSON.stringify({ name: newName }),
            });
            if (!response.ok) throw new Error("Failed to rename chatroom");
            const updatedChatroom: ChatRoom = await response.json();
            setChatrooms((prev) =>
                prev.map((chatroom) =>
                    chatroom.id === id ? updatedChatroom : chatroom
                )
            );
        } catch (error) {
            console.error("Error renaming chatroom:", error);
        }
    };

    useEffect(() => {
        fetchChatrooms();
    }, []);

    return (
        <ChatroomContext.Provider
            value={{
                chatrooms,
                createChatroom,
                deleteChatroom,
                renameChatroom,
            }}
        >
            {children}
        </ChatroomContext.Provider>
    );
};
