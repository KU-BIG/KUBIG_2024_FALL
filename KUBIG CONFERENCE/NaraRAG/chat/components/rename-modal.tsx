import React, { useState } from "react";
import { useToast } from "@/hooks/use-toast";

interface RenameModalProps {
    id?: string;
    isRenameOpen: boolean;
    onClose: () => void;
    onConfirm: (newName: string) => void;
    initialName: string;
}

const RenameModal: React.FC<RenameModalProps> = ({
    id,
    isRenameOpen,
    onClose,
    onConfirm,
    initialName,
}) => {
    const [chatroomName, setChatroomName] = useState(initialName);
    const [error, setError] = useState("");

    const { toast } = useToast();

    if (!isRenameOpen) return null;

    const handleConfirm = () => {
        const trimmedName = chatroomName.trim();

        if (!trimmedName) {
            setError("채팅방 이름을 입력하세요.");
            toast({
                description: "채팅방 이름을 입력하세요.",
            });
            return;
        }

        onConfirm(trimmedName);
    };

    return (
        <div
            id={id}
            className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-[9999]"
            onClick={(e) => e.stopPropagation()}
        >
            <div className="bg-white p-6 rounded shadow-lg w-[400]">
                <h2 className="text-lg font-semibold mb-4">채팅방 이름 수정</h2>
                <input
                    type="text"
                    value={chatroomName}
                    onChange={(e) => setChatroomName(e.target.value)}
                    className="w-full p-2 border rounded mb-4"
                    placeholder="채팅방 이름 입력"
                />
                {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

                <div className="flex justify-end space-x-2">
                    <button
                        className="px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600"
                        onClick={handleConfirm}
                    >
                        확인
                    </button>
                    <button
                        className="px-4 py-2 text-gray-600 bg-gray-200 rounded hover:bg-gray-300"
                        onClick={onClose}
                    >
                        취소
                    </button>
                </div>
            </div>
        </div>
    );
};

export default RenameModal;
