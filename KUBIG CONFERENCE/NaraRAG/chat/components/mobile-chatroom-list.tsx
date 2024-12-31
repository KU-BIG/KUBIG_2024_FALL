import React from "react";
import { useRouter, usePathname } from "next/navigation";
import { TrashIcon, Pencil } from "lucide-react";

import { ChatRoom } from "@prisma/client";

interface MobileChatroomListProps {
    chatrooms: ChatRoom[];
    onDeleteChatroom?: (id: string) => void;
    onRenameChatroom?: (chatroom: ChatRoom) => void;
    onChatroomClick: () => void;
}

const MobileChatroomList: React.FC<MobileChatroomListProps> = ({
    chatrooms,
    onDeleteChatroom,
    onRenameChatroom,
    onChatroomClick,
}) => {
    const router = useRouter();
    const pathname = usePathname();

    return (
        <div className="space-y-2 max-h-[400px]">
            {chatrooms.length === 0 ? (
                <p className="white align-middle">No chatrooms available</p>
            ) : (
                chatrooms.map((chatroom) => {
                    const isActive = pathname === `/chat/${chatroom.id}`;
                    return (
                        <div
                            key={chatroom.id}
                            className={`relative flex justify-between items-center cursor-pointer py-2 px-3 rounded ${
                                isActive
                                    ? "bg-[#b2d5ff] font-bold"
                                    : "hover:bg-[#ebf3ff]"
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
                                <div>
                                    <button
                                        className="text-gray-500 hover:text-red-400 ml-2"
                                        onClick={() => {
                                            if (onDeleteChatroom) {
                                                onDeleteChatroom(chatroom.id);
                                            }
                                        }}
                                    >
                                        <TrashIcon size={22} />
                                    </button>
                                    <button
                                        className="text-gray-500 hover:text-blue-400 ml-2"
                                        onClick={() => {
                                            if (onRenameChatroom) {
                                                onRenameChatroom(chatroom);
                                            }
                                        }}
                                    >
                                        <Pencil size={22} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    );
                })
            )}
        </div>
    );
};

export default MobileChatroomList;
