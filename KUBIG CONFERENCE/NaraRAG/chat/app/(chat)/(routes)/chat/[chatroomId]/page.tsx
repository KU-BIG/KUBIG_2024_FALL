import React from "react";
import prismadb from "@/lib/prismadb";
import { redirect } from "next/navigation";

import ChatClient from "@/app/(chat)/(routes)/chat/[chatroomId]/components/client";

interface ChatPageProps {
    params: {
        chatroomId: string;
    };
}

const ChatRoomPage = async ({ params }: ChatPageProps) => {
    try {
        const { chatroomId } = await params;

        if (!chatroomId) {
            redirect("/");
        }

        let chatroom = null;

        if (chatroomId === "guest") {
            // guest 채팅방은 데이터베이스에 존재하지 않으므로 가상 객체 생성
            chatroom = {
                id: "guest",
                name: "Guest Chat Room",
                createdAt: new Date(),
                updatedAt: new Date(),
                messages: [],
                _count: { messages: 0 },
            };
        } else {
            // 일반 채팅방 로드
            chatroom = await prismadb.chatRoom.findUnique({
                where: { id: chatroomId },
                include: {
                    messages: {
                        orderBy: { createdAt: "asc" },
                    },
                },
            });

            if (!chatroom) {
                redirect("/");
            }
        }

        return <ChatClient chatroom={chatroom} />;
    } catch (error) {
        console.error("Failed to fetch chatroom:", error);
        redirect("/");
    }
};

export default ChatRoomPage;
