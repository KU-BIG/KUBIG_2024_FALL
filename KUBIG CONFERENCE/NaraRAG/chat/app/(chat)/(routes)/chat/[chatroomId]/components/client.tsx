"use client";

import { ChatMessageProps } from "@/components/message";
import { ChatRoom, Message } from "@prisma/client";
import { FormEvent, useEffect, useState } from "react";

import ChatMessages from "@/components/messages";
import ChatForm from "@/components/chat-form";
import { useRouter } from "next/navigation";

import Image from "next/image";

interface ChatClientProps {
    chatroom?: ChatRoom & {
        messages: Message[];
        _count: {
            messages: number;
        };
    };
}

const ChatClient = ({ chatroom }: ChatClientProps) => {
    const router = useRouter();

    const initialMessages =
        chatroom?.messages.map((msg) => ({
            role: msg.role,
            content: msg.content,
        })) || [];

    const [messages, setMessages] =
        useState<ChatMessageProps[]>(initialMessages);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    // 데이터베이스에서 메시지를 불러옴
    useEffect(() => {
        const fetchMessages = async () => {
            if (!chatroom?.id) return;

            const token = localStorage.getItem("token");

            const res = await fetch(`/api/chat/${chatroom.id}/messages`, {
                headers: { Authorization: `Bearer ${token}` },
            });

            if (res.status === 404) {
                // 채팅방이 없으면 메인 페이지로 리다이렉트
                router.push("/");
                return;
            }

            if (!res.ok) {
                console.error("Failed to fetch messages");
                return;
            }

            const data = await res.json();

            if (data.messages) {
                setMessages(data.messages);
            }
        };

        fetchMessages();
    }, [chatroom?.id, router]);

    // 메시지를 전송하고 저장하는 시점
    const sendMessage = async (e: FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage: ChatMessageProps = { role: "user", content: input };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        // messages/route로 요청 전송
        try {
            console.log("sending req to messages/route");

            const token = localStorage.getItem("token");

            const res = await fetch(`/api/chat/${chatroom?.id}/messages`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    input: input,
                    chat_history: messages.map(({ role, content }) => ({
                        role,
                        content,
                    })),
                }),
            });

            if (!res.ok) {
                console.error(
                    "Server responded with an error:",
                    res.status,
                    await res.text()
                );
                throw new Error(`HTTP error! Status: ${res.status}`);
            }

            const data = await res.json().catch((error) => {
                console.error("Failed to parse JSON:", error);
                throw new Error("Invalid JSON response");
            });

            const systemMessage: ChatMessageProps = {
                role: "system",
                content: data.answer,
            };

            setMessages((prev) => [...prev, systemMessage]);

            if (!chatroom?.id) {
                console.error("Chatroom ID is missing");
                return;
            }
        } catch (error) {
            console.error("Failed to send message:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full mx-4 flex-1">
            <div className="flex flex-col align-middle items-center justify-center -z-40 absolute inset-0">
                <Image
                    src="/images/nararag-logo.png"
                    alt="NaraRAG"
                    width={450}
                    height={100}
                    className="opacity-50"
                />
            </div>
            <ChatMessages
                chatroom={chatroom!}
                isLoading={isLoading}
                messages={messages}
            />
            <ChatForm
                isLoading={isLoading}
                input={input}
                handleInputChange={(e) => setInput(e.target.value)}
                onSubmit={sendMessage}
            />
        </div>
    );
};

export default ChatClient;
