export interface CrontabValueObj {
  second?: string;
  min?: string;
  hour?: string;
  day?: string;
  month?: string;
  week?: string;
  year?: string;
}

export interface Week {
  key: number;
  value?: string;
}
