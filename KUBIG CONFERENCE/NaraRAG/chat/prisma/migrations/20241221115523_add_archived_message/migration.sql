-- CreateTable
CREATE TABLE "ArchivedMessage" (
    "id" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "chatroomId" TEXT NOT NULL,
    "chatroomName" TEXT NOT NULL,

    CONSTRAINT "ArchivedMessage_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "ArchivedMessage_chatroomId_idx" ON "ArchivedMessage"("chatroomId");

-- AddForeignKey
ALTER TABLE "ArchivedMessage" ADD CONSTRAINT "ArchivedMessage_chatroomId_fkey" FOREIGN KEY ("chatroomId") REFERENCES "ChatRoom"("id") ON DELETE CASCADE ON UPDATE CASCADE;
