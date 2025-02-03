'use client';
import Link from 'next/link';
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { NotebookPen } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background/95 relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(45rem_50rem_at_top,theme(colors.indigo.100),transparent)]" />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="text-center space-y-6 px-4"
      >
        <div className="flex items-center justify-center space-x-2 mb-8">
          <NotebookPen className="h-12 w-12 text-primary" />
          <h1 className="text-4xl font-bold">Notes</h1>
        </div>
        
        <h2 className="text-2xl font-medium text-muted-foreground max-w-[600px] mx-auto">
          Your thoughts and ideas, beautifully organized
        </h2>
        
        <p className="text-muted-foreground max-w-[600px]">
          A simple and elegant way to capture your thoughts, organize your life, and never forget anything.
        </p>

        <div className="flex gap-4 mt-8 justify-center">
          <Link href="/register">
            <Button size="lg" className="px-8">
              Get Started
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg" className="px-8">
              Sign In
            </Button>
          </Link>
        </div>

        <div className="mt-12 text-sm text-muted-foreground">
          Built with Next.js, Shadcn, and Django
        </div>
      </motion.div>
    </div>
  );
}