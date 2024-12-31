import React, { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { TrashIcon, MoreVertical, Pencil } from "lucide-react";

import Dropdown from "./dropdown-menu";

import { ChatRoom } from "@prisma/client";

interface ChatroomListProps {
    chatrooms: ChatRoom[];
    onDeleteChatroom?: (id: string) => void;
    onRenameChatroom?: (id: string) => void;
    onChatroomClick: () => void;
}

const ChatroomList: React.FC<ChatroomListProps> = ({
    chatrooms,
    onDeleteChatroom,
    onRenameChatroom,
    onChatroomClick,
}) => {
    const router = useRouter();
    const pathname = usePathname();

    const [activeMenu, setActiveMenu] = useState<string | null>(null);
    const [dropdownPosition, setDropdownPosition] = useState<{
        top: number;
        left: number;
    } | null>(null);

    // 메뉴 여닫기
    const handleToggleMenu = (event: React.MouseEvent, id: string) => {
        event.stopPropagation();

        if (activeMenu === id) {
            setActiveMenu(null);
            setDropdownPosition(null);
        } else {
            const rect = (event.target as HTMLElement).getBoundingClientRect();
            setActiveMenu(id);
            setDropdownPosition({
                top: rect.bottom + window.scrollY,
                left: rect.left + window.scrollX,
            });
        }
    };

    return (
        <div className="space-y-2 max-h-[400px]">
            {chatrooms.length === 0 ? (
                <p className="align-middle flex flex-col items-center pt-2">No chatrooms available</p>
            ) : (
                chatrooms.map((chatroom) => {
                    const isActive = pathname === `/chat/${chatroom.id}`;
                    return (
                        <div
                            key={chatroom.id}
                            className={`relative flex justify-between items-center cursor-pointer py-2 px-3 rounded ${
                                isActive
                                    ? "bg-[#9fcaff] font-bold"
                                    : "hover:bg-[#e7f0ff]"
                            }`}
                            onClick={() => {
                                if (!isActive) {
                                    router.push(`/chat/${chatroom.id}`);
                                }
                                onChatroomClick();
                            }}
                        >
                            <span className="text-[15px]">{chatroom.name}</span>
                            <div className="relative">
                                <button
                                    className="text-gray-500 hover:text-gray-400 ml-2"
                                    onClick={(e) =>
                                        handleToggleMenu(e, chatroom.id)
                                    }
                                >
                                    <MoreVertical size={22} />
                                </button>

                                {/* Dropdown Menu */}
                                {activeMenu === chatroom.id &&
                                    dropdownPosition && (
                                        <Dropdown
                                            isOpen={activeMenu === chatroom.id}
                                            position={dropdownPosition}
                                            onClose={() => setActiveMenu(null)}
                                        >
                                            <button
                                                onClick={() => {
                                                    if (onDeleteChatroom) {
                                                        onDeleteChatroom(
                                                            chatroom.id
                                                        );
                                                    }
                                                    setActiveMenu(null); // 메뉴 닫기
                                                }}
                                                className="flex items-center w-full px-4 py-2 text-sm text-red-500 hover:bg-red-50"
                                            >
                                                <TrashIcon
                                                    size={16}
                                                    className="mr-2"
                                                />
                                                Delete
                                            </button>
                                            <button
                                                className="flex items-center w-full px-4 py-2 text-sm text-blue-500 hover:bg-blue-50"
                                                onClick={() => {
                                                    if (onRenameChatroom) {
                                                        onRenameChatroom(
                                                            chatroom.id
                                                        );
                                                    }
                                                    setActiveMenu(null);
                                                }}
                                            >
                                                <Pencil
                                                    size={16}
                                                    className="mr-2"
                                                />
                                                Change Name
                                            </button>
                                        </Dropdown>
                                    )}
                            </div>
                        </div>
                    );
                })
            )}
        </div>
    );
};

export default ChatroomList;
