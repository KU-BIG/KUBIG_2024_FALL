"use client";

import Image from "next/image";
import React from "react";
import { useRouter } from "next/navigation";
import { useChatroomStore } from "@/store/chatroomStore";
import { ChatRoom } from "@prisma/client";

const MainPage = () => {
    const router = useRouter();
    const { createChatroom } = useChatroomStore();

    const handleStartChatting = async () => {
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
            createChatroom(guestChatroom);
            router.push(`/chat/${guestChatroom.id}`);
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

            const newChatroom: ChatRoom = await response.json();
            createChatroom(newChatroom);
            router.push(`/chat/${newChatroom.id}`);
        } catch (error) {
            console.error("Error creating chatroom:", error);
        }
    };

    return (
        <div className="flex flex-col h-full mx-4 pt-[110] flex-1 align-middle items-center ">
            <Image
                src="/images/nararag-logo.png"
                alt="NaraRAG"
                width={450}
                height={100}
                className="animate-image-up"
            />
            <div className="pt-[40px] text-[30px] animate-image-up  font-semibold ">
                <span>Welcome to </span>
                <span className=" text-[#7099ff] " style={
                    {
                        textShadow: "1px 2px 0px #afc6ff",
                    }
                }>NaraRAG</span>!
            </div>
            <button
                onClick={handleStartChatting}
                className="bg-[#7099ff] px-2 py-2 mt-[60] hover:bg-[#92c3ff] text-white rounded-md w-[200px]"
            >
                Start Chatting!
            </button>
        </div>
    );
};

export default MainPage;
