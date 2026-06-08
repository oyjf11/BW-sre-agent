import * as fs from 'fs';
import * as path from 'path';

const PROJECT_ROOT = process.cwd();
const TASKS_DIR = path.join(PROJECT_ROOT, '.tmp/tasks');

function ensureTaskDir() {
  if (!fs.existsSync(TASKS_DIR)) {
    fs.mkdirSync(TASKS_DIR, { recursive: true });
  }
}

function showStatus() {
  ensureTaskDir();
  let features: string[] = [];
  
  try {
    features = fs.readdirSync(TASKS_DIR).filter(f => {
      return fs.statSync(path.join(TASKS_DIR, f)).isDirectory() && f !== 'completed';
    });
  } catch (e) {
    console.log("No active tasks found.");
    return;
  }

  if (features.length === 0) {
    console.log("No active tasks found in .tmp/tasks/");
    return;
  }

  console.log("=== Current Task Status ===\n");
  features.forEach(feature => {
    const taskJsonPath = path.join(TASKS_DIR, feature, 'task.json');
    if (fs.existsSync(taskJsonPath)) {
      try {
        const taskData = JSON.parse(fs.readFileSync(taskJsonPath, 'utf-8'));
        const progress = taskData.subtask_count 
          ? Math.round((taskData.completed_count / taskData.subtask_count) * 100) 
          : 0;
        console.log(`[${feature}] ${taskData.name || 'Untitled'}`);
        console.log(`  Status: ${taskData.status} | Progress: ${progress}% (${taskData.completed_count}/${taskData.subtask_count})`);
      } catch (e) {
        console.log(`[${feature}] (Error parsing metadata)`);
      }
    } else {
        console.log(`[${feature}] (No metadata)`);
    }
  });
}

function createTask(feature: string, name: string, subtasks: string[]) {
  ensureTaskDir();
  
  const featureDir = path.join(TASKS_DIR, feature);
  if (!fs.existsSync(featureDir)) {
    fs.mkdirSync(featureDir, { recursive: true });
  }
  
  const taskData = {
    name,
    status: 'in_progress',
    subtask_count: subtasks.length,
    completed_count: 0,
    subtasks: subtasks.map((st, idx) => ({
      id: idx + 1,
      description: st,
      completed: false
    })),
    created_at: new Date().toISOString()
  };
  
  fs.writeFileSync(
    path.join(featureDir, 'task.json'),
    JSON.stringify(taskData, null, 2)
  );
  
  console.log(`✓ Created task [${feature}]: ${name}`);
  console.log(`  Subtasks (${subtasks.length}):`);
  subtasks.forEach((st, idx) => {
    console.log(`    ${idx + 1}. ${st}`);
  });
}

function showNext() {
  ensureTaskDir();
  let features: string[] = [];
  
  try {
    features = fs.readdirSync(TASKS_DIR).filter(f => {
      return fs.statSync(path.join(TASKS_DIR, f)).isDirectory() && f !== 'completed';
    });
  } catch (e) {
    console.log("No active tasks found.");
    return;
  }
  
  for (const feature of features) {
    const taskJsonPath = path.join(TASKS_DIR, feature, 'task.json');
    if (fs.existsSync(taskJsonPath)) {
      try {
        const taskData = JSON.parse(fs.readFileSync(taskJsonPath, 'utf-8'));
        const pendingSubtasks = taskData.subtasks?.filter((st: any) => !st.completed) || [];
        if (pendingSubtasks.length > 0) {
          console.log(`[${feature}] Next: ${pendingSubtasks[0].description}`);
          return;
        }
      } catch (e) {}
    }
  }
  console.log("No pending tasks found.");
}

function completeTask(feature: string, subtaskId: number, summary: string) {
  ensureTaskDir();
  
  const taskJsonPath = path.join(TASKS_DIR, feature, 'task.json');
  if (!fs.existsSync(taskJsonPath)) {
    console.log(`❌ Task [${feature}] not found.`);
    return;
  }
  
  try {
    const taskData = JSON.parse(fs.readFileSync(taskJsonPath, 'utf-8'));
    const subtask = taskData.subtasks.find((st: any) => st.id === subtaskId);
    
    if (!subtask) {
      console.log(`❌ Subtask ${subtaskId} not found in [${feature}].`);
      return;
    }
    
    if (subtask.completed) {
      console.log(`⚠️ Subtask ${subtaskId} already completed.`);
      return;
    }
    
    subtask.completed = true;
    subtask.summary = summary;
    taskData.completed_count = taskData.subtasks.filter((st: any) => st.completed).length;
    
    if (taskData.completed_count === taskData.subtask_count) {
      taskData.status = 'completed';
    }
    
    fs.writeFileSync(taskJsonPath, JSON.stringify(taskData, null, 2));
    console.log(`✓ Marked ${feature}/${subtaskId} as completed: ${summary}`);
  } catch (e) {
    console.log(`❌ Error: ${e}`);
  }
}

function getModifiedFiles(): string[] {
  try {
    const { execSync } = require('child_process');
    const output = execSync('git status --porcelain', { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'] });
    if (!output.trim()) return [];
    
    const files = output
      .split('\n')
      .filter(line => line.trim())
      .map(line => {
        const match = line.match(/^[A-Z]\s+(.+)$/);
        return match ? match[1] : null;
      })
      .filter((f): f is string => f !== null);
    
    return Array.from(new Set(files));
  } catch (e) {
    return [];
  }
}

const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'status':
    showStatus();
    break;
  case 'next':
    showNext();
    break;
  case 'create':
    if (args.length < 3) {
      console.log("Usage: task-management create <feature> <name> <subtask1> [subtask2] ...");
      process.exit(1);
    }
    const feature = args[1];
    const name = args[2];
    const subtasks = args.slice(3);
    createTask(feature, name, subtasks);
    break;
  case 'complete':
    if (args.length < 4) {
      console.log("Usage: task-management complete <feature> <subtaskId> <summary>");
      process.exit(1);
    }
    completeTask(args[1], parseInt(args[2]), args.slice(3).join(' '));
    break;
  default:
    console.log("Usage: task-management <status|next|create|complete> [args]");
    process.exit(1);
}