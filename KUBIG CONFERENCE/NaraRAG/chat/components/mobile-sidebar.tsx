"use client";

import React, { useState } from "react";
import { Sheet, SheetContent, SheetTitle, SheetTrigger } from "./ui/sheet";
import { Inbox, Menu, PenBox } from "lucide-react";
import { useRouter } from "next/navigation";

import ConfirmModal from "./modal";
import RenameModal from "./rename-modal";
import { ChatRoom } from "@prisma/client";
import MobileChatroomList from "./mobile-chatroom-list";

interface MobileSidebarProps {
    chatrooms: ChatRoom[];
    createChatroom: () => void;
    deleteChatroom: (id: string) => void;
    renameChatroom: (id: string, newName: string) => void;
}

const MobileSidebar: React.FC<MobileSidebarProps> = ({
    chatrooms,
    createChatroom,
    deleteChatroom,
    renameChatroom,
}) => {
    const router = useRouter();
    const [isExpanded, setIsExpanded] = useState(false);
    const [modalOpen, setModalOpen] = useState(false);
    const [isRenameModalOpen, setIsRenameModalOpen] = useState(false);
    const [selectedChatroom, setSelectedChatroom] = useState<ChatRoom | null>(
        null
    );
    const [selectedChatroomId, setSelectedChatroomId] = useState<string | null>(
        null
    );

    // 채팅방 삭제 모달 열기/닫기
    const openDeleteModal = (id: string) => {
        setSelectedChatroomId(id);
        setModalOpen(true);
    };

    const closeDeleteModal = () => {
        setSelectedChatroomId(null);
        setModalOpen(false);
    };

    const confirmDeleteChatroom = () => {
        if (selectedChatroomId) {
            deleteChatroom(selectedChatroomId);
            closeDeleteModal();
        }
    };

    // RenameModal 열기/닫기
    const openRenameModal = (chatroom: ChatRoom) => {
        setSelectedChatroom(chatroom);
        setIsRenameModalOpen(true);
    };

    const closeRenameModal = () => {
        setIsRenameModalOpen(false);
        setSelectedChatroom(null);
    };

    const handleRenameConfirm = (newName: string) => {
        if (selectedChatroom) {
            renameChatroom(selectedChatroom.id, newName);
            closeRenameModal();
        }
    };

    return (
        <Sheet open={isExpanded} onOpenChange={setIsExpanded}>
            <SheetTrigger className="md:hidden">
                <Menu size={28} />
            </SheetTrigger>

            <SheetContent
                side="left"
                className="w-[300] bg-gradient-to-br from-[#dcecff] via-[#dcecff] to-[#bedbff] z-[8000] pointer-events-auto"
            >
                <SheetTitle className="sr-only">Chatroom List</SheetTitle>
                <div>
                    <div className="relative flex gap-5">
                        {/* Add Chatroom */}
                        <div className="group">
                            <button
                                className="cursor-pointer transition-colors"
                                onClick={() => {
                                    createChatroom();
                                    setIsExpanded(false);
                                }}
                            >
                                <PenBox className="gray" size={30} />
                            </button>
                            <span className="absolute top-[55px] transform -translate-y-1/2 hidden group-hover:block bg-gray-800 text-white text-sm px-2 py-1 rounded-lg shadow-lg z-50">
                                Add Chatroom
                            </span>
                        </div>

                        {/* Archive */}
                        <div className="group">
                            <button
                                className="cursor-pointer transition-colors"
                                onClick={() => {
                                    router.push("/archive");
                                    setIsExpanded(false);
                                }}
                            >
                                <Inbox color="black" size={30} />
                            </button>
                            <span className="absolute top-[55px] transform -translate-y-1/2 hidden group-hover:block bg-gray-800 text-white text-sm px-2 py-1 rounded-lg shadow-lg z-50">
                                Archive
                            </span>
                        </div>
                    </div>
                </div>

                {/* Chatroom List */}
                <div className="flex flex-col h-full pt-10">
                    <MobileChatroomList
                        chatrooms={chatrooms}
                        onDeleteChatroom={openDeleteModal}
                        onRenameChatroom={openRenameModal}
                        onChatroomClick={() => setIsExpanded(false)}
                    />
                </div>
            </SheetContent>

            {/* Confirm Modal for Deletion */}
            <ConfirmModal
                isOpen={modalOpen}
                onClose={closeDeleteModal}
                onConfirm={confirmDeleteChatroom}
                title="채팅방 삭제"
                description="정말로 이 채팅방을 삭제하시겠습니까?"
            />

            {/* Rename Modal */}
            {isRenameModalOpen && selectedChatroom && (
                <RenameModal
                    id="rename-modal"
                    isRenameOpen={isRenameModalOpen}
                    onClose={closeRenameModal}
                    onConfirm={handleRenameConfirm}
                    initialName={selectedChatroom.name}
                />
            )}
        </Sheet>
    );
};

export default MobileSidebar;
