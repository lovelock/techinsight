---
title: "像PHP风格一样的Go Array"
description: 
date: 2024-07-25T14:12:47+08:00
image: 
math: 
license: 
hidden: false
comments: true
---

## Why?

The first programming language I've learnt is PHP and I love it today though I don't write it so frequently.

The most charming part of PHP is the design of **array**. It combines the concept of dict list in Python, someone would say it's not so clear but a man who has writen PHP for a long time would say **that's a fucking good design**.

Recently I've fallen in love with Golang because of its simplicity and readability. But there would be some awful times when it comes to retriet a value from a map. This project is designed for this.

## Usage

```golang
package main

import (
 "encoding/json"
 "fmt"

 array "github.com/lovelock/garray"
)

func main() {
 data := `{
  "name": "John Doe",
  "age": 30,
  "email": "john.doe@example.com",
  "isActive": true,
  "address": {
   "street": "123 Main St",
   "city": "Anytown",
   "state": "CA",
   "postalCode": "12345"
  },
  "phoneNumbers": [
   {
    "type": "home",
    "number": "555-555-5555"
   },
   {
    "type": "work",
    "number": "555-555-5556"
   }
  ],
  "projects": [
   {
    "name": "Project Alpha",
    "status": "completed",
    "tasks": [
     {
      "name": "Task 1",
      "dueDate": "2023-10-01",
      "completed": true
     },
     {
      "name": "Task 2",
      "dueDate": "2023-10-15",
      "completed": false
     }
    ]
   },
   {
    "name": "Project Beta",
    "status": "in progress",
    "tasks": [
     {
      "name": "Task 3",
      "dueDate": "2023-11-01",
      "completed": false
     },
     {
      "name": "Task 4",
      "dueDate": "2023-12-01",
      "completed": false
     }
    ]
   }
  ],
  "preferences": {
   "contactMethod": "email",
   "newsletterSubscribed": true,
   "languages": ["English", "Spanish", "German"]
  }
 }`

 var jsonMap map[string]any
 json.Unmarshal([]byte(data), &jsonMap)
 completed, err := array.Get(jsonMap, "projects", "1", "tasks", "1", "completed")
 if err != nil {
  fmt.Println("statusOfTheSecondTaskOfTheFirstProject: ", completed)
 }
}
```

## What problems does it solve

Imagine you've got a complex structure like this

```json
{
  "name": "John Doe",
  "age": 30,
  "email": "john.doe@example.com",
  "isActive": true,
  "address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "postalCode": "12345"
  },
  "phoneNumbers": [
    {
      "type": "home",
      "number": "555-555-5555"
    },
    {
      "type": "work",
      "number": "555-555-5556"
    }
  ],
  "projects": [
    {
      "name": "Project Alpha",
      "status": "completed",
      "tasks": [
        {
          "name": "Task 1",
          "dueDate": "2023-10-01",
          "completed": true
        },
        {
          "name": "Task 2",
          "dueDate": "2023-10-15",
          "completed": false
        }
      ]
    },
    {
      "name": "Project Beta",
      "status": "in progress",
      "tasks": [
        {
          "name": "Task 3",
          "dueDate": "2023-11-01",
          "completed": false
        },
        {
          "name": "Task 4",
          "dueDate": "2023-12-01",
          "completed": false
        }
      ]
    }
  ],
  "preferences": {
    "contactMethod": "email",
    "newsletterSubscribed": true,
    "languages": ["English", "Spanish", "German"]
  }
}
```

How can you check if the first projects second task is completed?

```golang
package main

import (
 "encoding/json"
 "fmt"
 "log"
)

// 定义JSON结构体
type Address struct {
 Street     string `json:"street"`
 City       string `json:"city"`
 State      string `json:"state"`
 PostalCode string `json:"postalCode"`
}

type PhoneNumber struct {
 Type   string `json:"type"`
 Number string `json:"number"`
}

type Task struct {
 Name      string `json:"name"`
 DueDate   string `json:"dueDate"`
 Completed bool   `json:"completed"`
}

type Project struct {
 Name   string `json:"name"`
 Status string `json:"status"`
 Tasks  []Task `json:"tasks"`
}

type Preferences struct {
 ContactMethod       string   `json:"contactMethod"`
 NewsletterSubscribed bool   `json:"newsletterSubscribed"`
 Languages           []string `json:"languages"`
}

type Person struct {
 Name         string        `json:"name"`
 Age          int           `json:"age"`
 Email        string        `json:"email"`
 IsActive     bool          `json:"isActive"`
 Address      Address       `json:"address"`
 PhoneNumbers []PhoneNumber `json:"phoneNumbers"`
 Projects     []Project     `json:"projects"`
 Preferences  Preferences   `json:"preferences"`
}

func main() {
 // JSON数据
 data := `{
  "name": "John Doe",
  "age": 30,
  "email": "john.doe@example.com",
  "isActive": true,
  "address": {
   "street": "123 Main St",
   "city": "Anytown",
   "state": "CA",
   "postalCode": "12345"
  },
  "phoneNumbers": [
   {
    "type": "home",
    "number": "555-555-5555"
   },
   {
    "type": "work",
    "number": "555-555-5556"
   }
  ],
  "projects": [
   {
    "name": "Project Alpha",
    "status": "completed",
    "tasks": [
     {
      "name": "Task 1",
      "dueDate": "2023-10-01",
      "completed": true
     },
     {
      "name": "Task 2",
      "dueDate": "2023-10-15",
      "completed": false
     }
    ]
   },
   {
    "name": "Project Beta",
    "status": "in progress",
    "tasks": [
     {
      "name": "Task 3",
      "dueDate": "2023-11-01",
      "completed": false
     },
     {
      "name": "Task 4",
      "dueDate": "2023-12-01",
      "completed": false
     }
    ]
   }
  ],
  "preferences": {
   "contactMethod": "email",
   "newsletterSubscribed": true,
   "languages": ["English", "Spanish", "German"]
  }
 }`

 var person Person

 // 解析JSON数据
 err := json.Unmarshal([]byte(data), &person)
 if err != nil {
  log.Fatalf("Error parsing JSON: %v", err)
 }

 // 获取第一个项目的第二个任务是否完成
 if len(person.Projects) > 0 && len(person.Projects[0].Tasks) > 1 {
  isCompleted := person.Projects[0].Tasks[1].Completed
  fmt.Printf("The second task of the first project is completed: %v\n", isCompleted)
 } else {
  fmt.Println("The required task does not exist.")
 }
}
```

Too complicated? What if you do not want define the structs in advance?

```golang
package main

import (
 "encoding/json"
 "fmt"
 "log"
)

func main() {
 // JSON数据
 data := `{
 ...
 }`

 // 定义一个用来存储JSON数据的map
 var result map[string]interface{}

 // 解析JSON数据到map
 err := json.Unmarshal([]byte(data), &result)
 if err != nil {
  log.Fatalf("Error parsing JSON: %v", err)
 }

 // 获取第一个项目的第二个任务是否完成
 projects, ok := result["projects"].([]interface{})
 if !ok || len(projects) == 0 {
  log.Fatalf("No projects found or format is incorrect")
 }

 firstProject, ok := projects[0].(map[string]interface{})
 if !ok {
  log.Fatalf("First project format is incorrect")
 }

 tasks, ok := firstProject["tasks"].([]interface{})
 if !ok || len(tasks) < 2 {
  log.Fatalf("No tasks found or insufficient tasks in the first project")
 }

 secondTask, ok := tasks[1].(map[string]interface{})
 if !ok {
  log.Fatalf("Second task format is incorrect")
 }

 completed, ok := secondTask["completed"].(bool)
 if !ok {
  log.Fatalf("Completed field is missing or not a boolean")
 }

 fmt.Printf("The second task of the first project is completed: %v\n", completed)
}

```

Holy shit! Too many template code. Now do you miss the PHP way?

```php
<?php

$jsonStr = <<<EOF
{
  "name": "John Doe",
  "age": 30,
  "email": "john.doe@example.com",
  "isActive": true,
  "address": {
   "street": "123 Main St",
   "city": "Anytown",
   "state": "CA",
   "postalCode": "12345"
  },
  "phoneNumbers": [
   {
    "type": "home",
    "number": "555-555-5555"
   },
   {
    "type": "work",
    "number": "555-555-5556"
   }
  ],
  "projects": [
   {
    "name": "Project Alpha",
    "status": "completed",
    "tasks": [
     {
      "name": "Task 1",
      "dueDate": "2023-10-01",
      "completed": true
     },
     {
      "name": "Task 2",
      "dueDate": "2023-10-15",
      "completed": false
     }
    ]
   },
   {
    "name": "Project Beta",
    "status": "in progress",
    "tasks": [
     {
      "name": "Task 3",
      "dueDate": "2023-11-01",
      "completed": false
     },
     {
      "name": "Task 4",
      "dueDate": "2023-12-01",
      "completed": false
     }
    ]
   }
  ],
  "preferences": {
   "contactMethod": "email",
   "newsletterSubscribed": true,
   "languages": ["English", "Spanish", "German"]
  }
 }
EOF;

$json = json_decode($jsonStr, true);
$statusOfTheSecondTaskOfTheFirstProject = $json['projects'][1]['completed'] ?? false;

var_dump($statusOfTheSecondTaskOfTheFirstProject);

var_dump(isset($json['projects'][2]['completed']));
```

In PHP you don't have to check the validatbility of every level and you can use `isset` to check only the target key.

In golang operators are not allowed to be overrided, so we can use variant variables.

## Examples

See the `*_test.go` files.
