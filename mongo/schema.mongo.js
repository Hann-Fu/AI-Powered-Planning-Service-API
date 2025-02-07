const mongoose = require('mongoose');
const { Schema } = mongoose;

// 1) Sub schemas for schedules
// A. YmdSchema => Used in SpecificType
const YmdSchema = new Schema({
  date: {
    type: String,
    required: true,
    description: 'The date of the task in YYYY-MM-DD format'
  }
}, { _id: false });

// B. SpecificType => specific: list[Ymd]
const SpecificTypeSchema = new Schema({
  specific: {
    type: [YmdSchema],
    required: true,
    description: 'Specify dates for this task'
  }
}, { _id: false });

// C. OnWorkdayType => on_workday: list[int]
const OnWorkdayTypeSchema = new Schema({
  on_workday: {
    type: [Number],
    required: true,
    description: 'Weekdays for the task (1=Mon ... 5=Fri)'
  }
}, { _id: false });

// D. OnWeekendType => on_weekend: list[int]
const OnWeekendTypeSchema = new Schema({
  on_weekend: {
    type: [Number],
    required: true,
    description: 'Weekends for the task (1=Sat, 2=Sun)'
  }
}, { _id: false });

// E. OnWeekdayType => on_weekday: list[int]
const OnWeekdayTypeSchema = new Schema({
  on_weekday: {
    type: [Number],
    required: true,
    description: 'Days of the week for the task (1=Mon ... 5=Fri, etc.)'
  }
}, { _id: false });

// F. OnMonthdayType => on_monthday: list[int]
const OnMonthdayTypeSchema = new Schema({
  on_monthday: {
    type: [Number],
    required: true,
    description: 'Month days for the task (1 = first day, etc.)'
  }
}, { _id: false });

// G. PeriodicType => periodic: int
const PeriodicTypeSchema = new Schema({
  periodic: {
    type: Number,
    required: true,
    description: 'Period of the task in days'
  }
}, { _id: false });

// 2) Union of Schedules -> We'll add a small discriminator field `schedule_type`
const ScheduleUnionSchema = new Schema({
  schedule_type: {
    type: String,
    enum: [
      'Specific',
      'On workday',
      'On Weekend',
      'On weekday',
      'On monthday',
      'Periodic'
    ],
    required: true,
    description: 'Indicates which schedule sub-schema is used'
  },
  specificType: SpecificTypeSchema,
  onWorkdayType: OnWorkdayTypeSchema,
  onWeekendType: OnWeekendTypeSchema,
  onWeekdayType: OnWeekdayTypeSchema,
  onMonthdayType: OnMonthdayTypeSchema,
  periodicType: PeriodicTypeSchema
}, { _id: false });

// 3) Subschemas for single vs. across time attributes

// A. SingleTimeAttribute => { date: str }
const SingleTimeAttributeSchema = new Schema({
  date: {
    type: String,
    required: true,
    description: 'The date of the task in YYYY-MM-DD format'
  }
}, { _id: false });

// B. AcrossTimeAttribute => { start_date, end_date, repeat, schedule }
const AcrossTimeAttributeSchema = new Schema({
  start_date: {
    type: String,
    required: true,
    description: 'Start date of the task in YYYY-MM-DD format'
  },
  end_date: {
    type: String,
    required: true,
    description: 'End date of the task in YYYY-MM-DD format'
  },
  repeat: {
    type: String,
    enum: [
      'Specific',
      'Everyday',
      'On workday',
      'On Weekend',
      'On weekday',
      'On monthday',
      'Periodic'
    ],
    required: true,
    description: 'The repeat type of the task'
  },
  schedule: {
    type: ScheduleUnionSchema,
    required: true,
    description: 'The schedule object (sub-schema) matching the repeat type'
  }
}, { _id: false });

// 4) Union of SingleTimeAttribute & AcrossTimeAttribute
//    We'll add a `duration_type` field to indicate which sub-schema is used.
const TaskDurationUnionSchema = new Schema({
  duration_type: {
    type: String,
    enum: ['single', 'across'],
    required: true,
    description: 'Indicates which time attribute schema is used'
  },
  singleTime: SingleTimeAttributeSchema,
  acrossTime: AcrossTimeAttributeSchema
}, { _id: false });

// 5) Quantization => { progress_start, goal }
const QuantizationSchema = new Schema({
  progress_start: {
    type: Number,
    required: true,
    description: 'The start progress of the task'
  },
  goal: {
    type: Number,
    required: true,
    description: 'The goal of the task'
  }
}, { _id: false });

// 6) TimeSeriesTask => main task info
const TimeSeriesTaskSchema = new Schema({
  task_name: {
    type: String,
    required: true,
    description: 'The name of the task'
  },
  description: {
    type: String,
    required: true,
    description: 'The description of the task'
  },
  task_duration: {
    type: TaskDurationUnionSchema,
    required: true,
    description: 'Union of SingleTimeAttribute and AcrossTimeAttribute'
  },
  time_in_day: {
    type: String,
    required: true,
    description: 'Time in HH:MM format'
  },
  quantization: {
    type: QuantizationSchema,
    required: false,
    description: 'Optional quantization object'
  },
  notes: {
    type: String,
    required: true,
    description: 'Notes for the task'
  }
}, { _id: false });

// 7) The top-level Tasks schema
const TasksSchema = new Schema({
  tasks_name: {
    type: [String],
    required: true,
    description: 'The name(s) of the tasks'
  },
  tasks: {
    type: [TimeSeriesTaskSchema],
    required: true,
    description: 'The list of tasks with time-series attributes'
  }
});

// Export a model called "Tasks"
module.exports = mongoose.model('Tasks', TasksSchema);
