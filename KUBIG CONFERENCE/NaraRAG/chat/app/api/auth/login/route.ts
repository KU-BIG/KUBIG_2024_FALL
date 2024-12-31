import { NextResponse } from "next/server";
import prismadb from "@/lib/prismadb";

import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

export async function POST(req: Request) {
    try {
        const { email, password } = await req.json();

        // 이메일로 사용자 찾기
        const user = await prismadb.user.findUnique({
            where: { email },
        });

        if (!user) {
            return NextResponse.json(
                { error: "해당 이메일의 사용자가 존재하지 않습니다." },
                { status: 401 }
            );
        }

        // 비밀번호 검증
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            return NextResponse.json(
                { error: "비밀번호가 일치하지 않습니다." },
                { status: 401 }
            );
        }

        // JWT 토큰 생성
        const secretKey = process.env.JWT_SECRET || "secret"; // 환경 변수에서 시크릿 키 가져오기
        const token = jwt.sign(
            {
                id: user.id,
                email: user.email,
            },
            secretKey,
            {
                expiresIn: "7h",
            }
        );

        // 로그인 성공
        const response = NextResponse.json({
            user: {
                id: user.id,
                email: user.email,
            },
            token,
        });

        // HttpOnly 쿠키에 JWT 저장
        response.cookies.set("token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "strict",
            path: "/",
            maxAge: 60 * 60 * 7, // 7시간
        });

        return response;
    } catch (error) {
        console.error(error);
        return NextResponse.json(
            { error: "로그인 처리 중 오류가 발생했습니다." },
            { status: 500 }
        );
    }
}
