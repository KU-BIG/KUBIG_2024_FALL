import { NextRequest } from "next/server";
import jwt from "jsonwebtoken";

export function getUserIdFromRequest(req: NextRequest): string | null {
    const authHeader = req.headers.get("Authorization");

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        console.error("Authorization 헤더가 없습니다.");
        return null;
    }

    const token = authHeader.split(" ")[1];
    if (!token) return null;

    try {
        const secretKey = process.env.JWT_SECRET || "secret";
        const decoded = jwt.verify(token, secretKey) as { id: string };
        return decoded.id;
    } catch (error) {
        console.error("JWT 인증 실패:", error);
        return null;
    }
}
