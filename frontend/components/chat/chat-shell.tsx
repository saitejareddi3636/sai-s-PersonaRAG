import type { ReactNode } from "react";

import { RecruiterSnapshot } from "@/components/profile 2/recruiter-snapshot";

type ChatShellProps = {
  children: ReactNode;
  className?: string;
};

/**
 * Side-by-side recruiter snapshot + main column. Stacks on small screens.
 */
export function ChatShell({ children, className = "" }: ChatShellProps) {
  return (
    <div
      className={`mx-auto flex max-w-6xl flex-col gap-8 lg:flex-row lg:items-start lg:gap-10 ${className}`}
    >
      <RecruiterSnapshot className="w-full shrink-0 lg:sticky lg:top-[4.5rem] lg:w-[280px]" />
      <div className="min-w-0 flex-1">{children}</div>
    </div>
  );
}
