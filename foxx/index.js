'use strict';

const createRouter = require('@arangodb/foxx/router');
const router = createRouter();
module.context.use(router);

const joi = require('joi');
const queues = require('@arangodb/foxx/queues');
const queue = queues.create('puller-scheduler');
const process_queue = queues.create('task-processor');
const db = require('@arangodb').db;

// Start execution of puller
router.get('/execute/:id/:user_id/:mode', function (req, res) {
  if (!db._collection("ScheduleIntervalSettings").exists(req.pathParams.id)) {
    res.send('settings does not exist with the given id');
  } else {
    try {
      var interval_obj = db._collection("ScheduleIntervalSettings").document(req.pathParams.id)
      var account_obj = db._collection("AwsCredentials").document(interval_obj.account_id)
      if (req.pathParams.mode == "edit") {
        queue.delete(interval_obj.foxx_job_id)
      }

      var job = queue.push(
        {
          mount: '/foxx',
          name: 'execute-scheduler',
          maxFailures: 0
        },
        {
          external_id: account_obj.external_id,
          role_arn: account_obj.role_arn,
          service: interval_obj.service,
          user_id: req.pathParams.user_id,
          interval_id: interval_obj._id,
          account_id: account_obj._id
        },
        {
          repeatDelay:  interval_obj.repeat_delay * 1000*60,
          repeatTimes: Infinity,
          success: function(result, jobData, job) {
            if (result.status == 201) {
              const db = require('@arangodb').db;
              result_body = JSON.parse(result.body)
              // Inserting data into collection
              job_exist = db._collection("Jobs").firstExample("foxx_job_id", job._id)
              if (job_exist != null) {
                data = {
                  "celery_job_id": result_body.task_id,
                  "time_ran": result_body.time_ran,
                  "celery_status": result_body.state
                }
                query = 'FOR doc IN Jobs\
                            FILTER doc._id == "'+job_exist._id+'"\
                              UPDATE doc WITH { celery: APPEND(doc.celery, '+JSON.stringify(data)+')} IN Jobs'
                db._query(query)
              } else {
                db._collection("Jobs").insert({
                  "foxx_job_id": job._id,
                  "foxx_status": job.status,
                  "interval_id": jobData.interval_id,
                  "account_id": jobData.account_id,
                  "celery": [{
                    "celery_job_id": result_body.task_id,
                    "time_ran": result_body.time_ran,
                    "celery_status": result_body.state
                  }]
                })
              }
            }
          }
        }
      );
      db._collection("ScheduleIntervalSettings").update(req.pathParams.id, {
        "foxx_job_id": job
      })
      res.send({'status': true, 'job_id': job})
    } catch(e) {
      res.send({'status': false, 'msg': e})
    }
  }
})
.pathParam('id', joi.string().required(), 'Settings id required')
.pathParam('user_id', joi.string().required(), 'user id required')
.pathParam('mode', joi.string().optional(), 'new/edit can be any value')
.response(['text/plain'], 'Task id.')
.summary('Execute periodic task for puller')
.description('The GET API accepts the scheduler setting id as a parameter to get the \
  scheduler settings from database and will create Job for puller');

// *****************************************************************************

// Fetch Job from queue
router.get('/retrieve/:id', function (req, res) {
  res.send(JSON.stringify(queue.get(req.pathParams.id)));
})
.pathParam('id', joi.string().required(), 'Job id required')
.response(['text/plain'], 'object.')
.summary('Fetching a job from the queue')
.description('Returns the job for the given jobId. Properties of the job object \
will be fetched whenever they are referenced and can not be modified.');

// *****************************************************************************

// Get all task from scheduler
router.get('/get-all', function (req, res) {
  res.send(queue.all());
})
.response(['text/plain'], 'Array.')
.summary('Fetching an array of all jobs in a queue')
.description('Returns an array of job ids of all jobs in the given queue, \
optionally filtered by the given job type. The jobs will be looked up in the\
specified queue in the current database.');

// *****************************************************************************

// Get all in progress jobs
router.get('/progress', function (req, res) {
  res.send(queue.progress());
})
.response(['text/plain'], 'Array.')
.summary('Fetching an array of jobs that are currently in progress')
.description('Returns an array of job ids of jobs in the given queue with the \
status "progress", optionally filtered by the given job type');

// *****************************************************************************

// Get all completed jobs
router.get('/completed', function (req, res) {
  res.send(queue.complete());
})
.response(['text/plain'], 'Array.')
.summary('Fetching an array of completed jobs in a queue')
.description('Returns an array of job ids of jobs in the given queue with the \
status "complete", optionally filtered by the given job type');

// *****************************************************************************

// Get all failed jobs
router.get('/failed', function (req, res) {
  res.send(queue.failed());
})
.response(['text/plain'], 'Array.')
.summary('Fetching an array of failed jobs in a queue')
.description('Returns an array of job ids of jobs in the given queue with the \
status "failed", optionally filtered by the given job type');

// *****************************************************************************

// Get all in pending jobs
router.get('/pending', function (req, res) {
  res.send(queue.pending());
})
.response(['text/plain'], 'Array.')
.summary('Fetching an array of pending jobs in a queue')
.description('Returns an array of job ids of jobs in the given queue with the \
status "pending", optionally filtered by the given job type');

// *****************************************************************************

// delete task from scheduler
router.get('/delete/:id', function (req, res) {
  res.send(queue.delete(req.pathParams.id));
})
.pathParam('id', joi.string().required(), 'Settings id required')
.response(['text/plain'], 'Boolean.')
.summary('Deleting a job from the queue')
.description('Deletes a job with the given job id. The job will be looked up and\
 deleted in the specified queue in the current database.');

// *****************************************************************************

// Task processor
router.get('/processor/:id', function (req, res) {
  try {
    var state_obj = db._collection("Jobs").document(req.pathParams.id)
    var job = process_queue.push(
      {
        mount: '/foxx',
        name: 'task-processor',
      },
      {
        account_id: state_obj.account_id,
        state_id: state_obj.id,
        service: "iam"//schedule_obj.process_service,
      },
      {
          success: function(result, jobData, job) {
            if (result.status == 201) {
              const db = require('@arangodb').db;
              result_body = JSON.parse(result.body)
              // Inserting data into collection
              db._collection("Jobs").insert({
                "foxx_job_id": job._id,
                "foxx_status": job.status,
                "time_ran": result_body.time_ran,
                "account_id": jobData.account_id,
              })
            }
          }
      }
    );
    res.send(job)
  } catch(e) {
    throw e
  }
})
.response(['text/plain'], '')
.pathParam('id', joi.string().required(), 'State id required')
.summary('Task Processor')
.description('The POST API for task processor');


// *****************************************************************************

// Task Puller
router.post('/puller', function (req, res) {
  try {
    var job = queues.create('task-puller').push({
        mount: '/foxx',
        name: 'task-puller',
      },{
        external_id: req.body.external_id,
        role_arn: req.body.role_arn,
        service: req.body.service,
        user: req.body.user,
      },
      {
          success: function(result, jobData, job) {
            if (result.status == 201) {
              const db = require('@arangodb').db;
              result_body = JSON.parse(result.body)
              // Inserting data into collection
              db._collection("Jobs").insert({
                "foxx_job_id": job._id,
                "foxx_status": job.status,
                "celery": [{
                  "time_ran": result_body.time_ran,
                  "celery_job_id": result_body.task_id,
                  "celery_status": result_body.state,
                }]
              })
            }
          },
          failed: function(result, jobData, job) {
            console.log("I am in failed job")
          }
      }
    );
    res.send(job)
  } catch(e) {
    throw e
  }
})
.response(['text/plain'], 'Plain Text')
.body(joi.object().keys({
  external_id: joi.string().required(),
  role_arn: joi.string().required(),
  service: joi.string().required(),
  user: joi.number().required(),
}))
.summary('Task Puller')
.description('The POST API that will hit Puller');

// *****************************************************************************

// Task Puller
router.post('/update-state', function (req, res) {
  var id = req.body.interval_id
  var task_id = req.body.celery_job_id
  var status = req.body.celery_status
  var host = req.body.puller_host
  var reason = req.body.reason
  try {
    var data = reason != undefined ? 'MERGE(element, { celery_status: "'+status+'", puller_host: "'+host+'", reason: "'+reason+'" })' : 'MERGE(element, { celery_status: "'+status+'", puller_host: "'+host+'" })'
    if (id != '') {
      var query_line = 'FOR document in Jobs  \
                            FILTER document.interval_id == "'+id+'"\
                            LET alteredList = (FOR element IN document.celery  \
                                 LET newItem = (element.celery_job_id == "'+task_id+'" ? '+data+': element)    \
                                 RETURN newItem)  \
                            UPDATE document WITH { celery:  alteredList } IN Jobs \
                            return document._id'
    } else {
      var query_line = 'FOR document in Jobs  \
                            LET alteredList = (FOR element IN document.celery  \
                                 LET newItem = (element.celery_job_id == "'+task_id+'" ?  '+data+': element)    \
                                 RETURN newItem)  \
                            UPDATE document WITH { celery:  alteredList } IN Jobs \
                            return document._id'
    }
    db._query(query_line)
    res.status(200).json({'msg': true})
  } catch(e) {
    res.status(400).json({'msg': e})
  }
})
.response(['text/plain'], 'Plain Text')
.body(joi.object().keys({
  interval_id: joi.string().allow('').optional(),
  celery_job_id: joi.string().required(),
  celery_status: joi.string().required(),
  puller_host: joi.string().required(),
  reason: joi.string().optional(),
}))
.summary('Puller State Update')
.description('The POST API update the state of Jobs');
