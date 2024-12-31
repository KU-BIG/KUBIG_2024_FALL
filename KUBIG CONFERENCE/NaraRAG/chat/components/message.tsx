"use client";

import { cn } from "../lib/utils";
import { BeatLoader } from "react-spinners";
import { useTheme } from "next-themes";
import { useToast } from "../hooks/use-toast";
import { Button } from "./ui/button";
import { MoreVertical, Copy, Inbox } from "lucide-react";

import BotAvatar from "./bot-avatar";
import UserAvatar from "./user-avatar";
import { useEffect, useState, useRef } from "react";

export interface ChatMessageProps {
    role: "system" | "user";
    content?: string;
    isLoading?: boolean;
    src?: string;
    chatroomId?: string;
    chatroomName?: string;
    userId?: string;
}

const ChatMessage = ({
    role,
    content = "",
    isLoading,
    chatroomId,
    chatroomName,
    userId,
}: ChatMessageProps) => {
    const { toast } = useToast();
    const { theme } = useTheme();

    const [dropdownOpen, setDropdownOpen] = useState(false);
    const [dropdownVisible, setDropdownVisible] = useState(false);

    const dropdownRef = useRef<HTMLDivElement>(null);

    // Dropdown 토글
    const toggleDropdown = () => {
        if (dropdownVisible) {
            setDropdownOpen(false);
            setTimeout(() => setDropdownVisible(false), 300);
        } else {
            setDropdownVisible(true);
            setTimeout(() => setDropdownOpen(true), 0); // 바로 열기 시작
        }
    };

    const closeDropdown = () => {
        setDropdownOpen(false);
        setTimeout(() => setDropdownVisible(false), 300);
    };

    useEffect(() => {
        const handleOutsideClick = (event: MouseEvent) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target as Node)
            ) {
                closeDropdown();
            }
        };

        document.addEventListener("click", handleOutsideClick);
        return () => {
            document.removeEventListener("click", handleOutsideClick);
        };
    }, []);

    const onCopy = () => {
        if (!content) {
            return;
        }

        navigator.clipboard.writeText(content);
        toast({
            description: "Messages copied to clipboard",
        });
    };

    const onArchive = async () => {
        try {
            const response = await fetch("/api/archive", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    content,
                    chatroomId,
                    chatroomName,
                    userId,
                }),
            });

            if (!response.ok) {
                throw new Error("Failed to archive message");
            }

            toast({
                description: "Message archived!",
            });
        } catch (error) {
            console.error("Error archiving message:", error);
            toast({
                description: "Failed to archive message",
                variant: "destructive",
            });
            return;
        }
    };

    const formatContent = (text: string) => {
        text = text.replace(/(\(출처:\s*https?:\/\/)/g, "\n$1");

        const lines = text.split("\n");

        const urlRegex = /(https?:\/\/[^\s)]+)/gi;

        return lines.map((line, lineIndex) => {
            const elements: (string | JSX.Element)[] = [];

            let lastIndex = 0;
            let match;
            while ((match = urlRegex.exec(line)) !== null) {
                const url = match[0];
                const start = match.index;
                const end = start + url.length;

                if (start > lastIndex) {
                    elements.push(line.slice(lastIndex, start));
                }

                elements.push(
                    <a
                        key={`link-${lineIndex}-${start}`}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 underline"
                    >
                        {url}
                    </a>
                );

                lastIndex = end;
            }

            if (lastIndex < line.length) {
                elements.push(line.slice(lastIndex));
            }

            return (
                <span key={lineIndex}>
                    {elements}
                    <br />
                </span>
            );
        });
    };

    return (
        <div
            className={cn(
                "group flex items-start gap-x-3 py-6 w-full transition-transform duration-500 ease-in-out",
                role === "user" ? "justify-end" : "justify-start",
                "animate-message-up"
            )}
        >
            {role !== "user" && <BotAvatar />}
            <div
                className={cn(
                    "mt-[3] rounded-md px-5 py-4 max-w-lg text-sm bg-gradient-to-b from-[#dedfff] via-[#e9eaff] to-[#f8f9fd] transition-all duration-300 shadow-md break-words",
                    "animate-expand-height"
                )}
            >
                {isLoading ? (
                    <BeatLoader
                        size={5}
                        color={theme === "light" ? "black" : "white"}
                    />
                ) : (
                    formatContent(content || "")
                )}
            </div>

            {role === "user" && <UserAvatar />}

            {role !== "user" && !isLoading && (
                <div className="relative" ref={dropdownRef}>
                    {/* Dropdown 버튼 */}
                    <Button
                        onClick={(e) => {
                            e.stopPropagation(); // 클릭 이벤트 전파 방지
                            toggleDropdown();
                        }}
                        className="opacity-0 group-hover:opacity-100 transition"
                        size="icon"
                        variant="ghost"
                    >
                        <MoreVertical />
                    </Button>

                    {/* Dropdown 메뉴 */}
                    {dropdownVisible && (
                        <div
                            id="dropdown"
                            className={cn(
                                "absolute left-5 mt-2 w-40 bg-white border rounded shadow-lg z-10",
                                "transition-all duration-300 ease-in-out",
                                dropdownOpen
                                    ? "opacity-100 scale-100"
                                    : "opacity-0 scale-95"
                            )}
                            onClick={(e) => e.stopPropagation()} // 클릭 이벤트 전파 방지
                        >
                            <button
                                onClick={() => {
                                    onCopy();
                                    closeDropdown(); // 드롭다운 닫기
                                }}
                                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                                <Copy size={15} className="mr-2" />
                                <span className="text-[13px] ">
                                    Copy Message
                                </span>
                            </button>

                            <button
                                onClick={() => {
                                    onArchive();
                                    closeDropdown();
                                }}
                                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                            >
                                <Inbox size={15} className="mr-2" />
                                <span className="text-[13px] ">Archive</span>
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default ChatMessage;
