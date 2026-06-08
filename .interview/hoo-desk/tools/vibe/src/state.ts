import * as fs from 'fs';
import { Task, TaskFile, TaskFileSchema } from './contracts';

const byPrioritySeq = (a: Task, b: Task) => a.priority - b.priority || a.seq - b.seq;

export function selectNext(tasks: Task[]): Task | null {
  const doing = tasks.filter((t) => t.status === 'doing').sort(byPrioritySeq);
  if (doing.length > 0) return doing[0];
  const pending = tasks.filter((t) => t.status === 'pending').sort(byPrioritySeq);
  if (pending.length > 0) return pending[0];
  return null;
}

const ALLOWED: Record<Task['status'], Task['status'][]> = {
  pending: ['doing'],
  doing: ['passing', 'failing', 'pending'],
  passing: [],
  failing: ['doing'],
};

export function transition(task: Task, to: Task['status']): Task {
  if (!ALLOWED[task.status].includes(to)) {
    throw new Error(`illegal transition ${task.status} -> ${to}`);
  }
  return { ...task, status: to };
}

export function loadTaskFile(filePath: string): TaskFile {
  try {
    return TaskFileSchema.parse(JSON.parse(fs.readFileSync(filePath, 'utf-8')));
  } catch (e: any) {
    throw new Error(`failed to load task file at ${filePath}: ${e.message}`);
  }
}

export function saveTaskFile(filePath: string, tf: TaskFile): void {
  fs.writeFileSync(filePath, JSON.stringify(tf, null, 2));
}
