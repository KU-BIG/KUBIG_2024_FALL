import ReactDOM from "react-dom";
import React, { useState, useEffect } from "react";

interface DropdownProps {
    isOpen: boolean;
    children: React.ReactNode;
    position: { top: number; left: number }; // 드롭다운 위치
    onClose?: () => void;
}

const Dropdown: React.FC<DropdownProps> = ({
    isOpen,
    children,
    position,
}) => {
    const [dropdownOpen, setDropdownOpen] = useState(false); // 완전히 열린 상태
    const [dropdownVisible, setDropdownVisible] = useState(false); // DOM에서 보이는 상태

    useEffect(() => {
        if (isOpen) {
            setDropdownVisible(true); // DOM에 렌더링
            setTimeout(() => setDropdownOpen(true), 0); // 애니메이션 시작
        } else {
            setDropdownOpen(false); // 닫힘 애니메이션 시작
            const timer = setTimeout(() => setDropdownVisible(false), 300); // 300ms 후 DOM에서 제거
            return () => clearTimeout(timer);
        }
    }, [isOpen]);

    if (!dropdownVisible) return null; // 완전히 닫힌 후 DOM에서 제거

    return ReactDOM.createPortal(
        <div
            className={`absolute bg-white border rounded shadow-lg z-[9999] transition-all duration-300 ease-in-out ${
                dropdownOpen ? "opacity-100 scale-100" : "opacity-0 scale-95"
            }`}
            style={{
                top: position.top,
                left: position.left,
            }}
            onClick={(e) => e.stopPropagation()} // 드롭다운 내부 클릭 시 이벤트 전파 방지
        >
            {children}
        </div>,
        document.body // body 최상위에 렌더링
    );
};

export default Dropdown;
