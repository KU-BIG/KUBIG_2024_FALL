import { NextResponse } from "next/server";
import jwt from "jsonwebtoken";

export function middleware(req: Request) {
    const authHeader = req.headers.get("Authorization");

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return NextResponse.json(
            { error: "인증 토큰이 필요합니다." },
            { status: 401 }
        );
    }

    const token = authHeader.split(" ")[1];
    const secretKey = process.env.JWT_SECRET || "your-secret-key";

    try {
        jwt.verify(token, secretKey);
        return NextResponse.next(); // 요청 통과
    } catch (error) {
        return NextResponse.json(
            { error: "유효하지 않은 토큰입니다." },
            { status: 401 }
        );
    }
}

export const config = {
    matcher: ["/api/protected/:path*"], // "/api/protected" 경로 하위 모두에 적용
};
