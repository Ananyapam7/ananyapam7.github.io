---
layout: post
title: Threading in C++
date: 2023-07-15 15:09:00
description: Revise threading in depth
tags: finance code
categories: tech
featured: true
---

# Introduction

Threading is a concept in C++ 11 and we will cover the following:
- What is Threading? What are threads and ways to create them?
- join and detach
- Mutex, Race Conditiion and Critical Section
- Types of Mutex and locks
- Condition Variables
- Thread Synchronization
- Producer Consumer Problem

Thread is a lighweight process. To use them, we need to include the ```#include <thread>```. The ```main()``` is the only thread if we don't have any other threads. Threads are created inside the ```main()``` function. 

Applications:
- MS word uses threads, one for formatting, one for spell check etc
- New tabs in browsers are opened in new threads
- VScode uses threading for autocomplete (intellisense)

Here's a basic C++ threading program:

```c++
#include <iostream>
#include <thread>

void threadFunction(int threadNumber) {
    std::cout << "Thread " << threadNumber << " is running\n";
}

int main() {
    // thread requires a callable object
    std::thread t1(threadFunction, 1);
    std::thread t2(threadFunction, 2);

    // Joining the threads with the main thread
    t1.join();
    t2.join();

    std::cout << "Both threads have completed their execution\n";

    return 0;
}
```

Note that now t1 and t2 are two independent threads. But when we see ```t1.join()```, it will **wait** for the execution of t1 to complete and join the thread t1 to the main. Next ```t2.join()``` will wait for t2 to complete and join the thread t2 to main. A big point to note here is that it is NOT TRUE that t1 will be created before t2. When creating mutliple threads together, it is not guranteed that they are created in order. This was an example of thread creation using function pointer. There are several other ways to create threads as well. A thread requires a callable object.

# Creating Threads in C++ 11
- Function Pointer
- Lambda Function
- Functor / Function Object: A function wrapped in a class so it can be used as an object. grater<int>()
- Non-Static Member Function
- Static Member Function

Here's an example of threading with a lambda function:

```c++
int main(){
    auto fun = [](int x){
        while(x-- >0){
            cout<<x<<endl;
        }
    };

    std::thread t(fun, 10);
    t.join();
    return 0;
}
```

which can also be done this way:

```c++
int main(){
    std::thread t(
    [](int x){
        while(x-- >0){
            cout<<x<<endl;
        }
    }, 10);
    t.join();
    return 0;
}
```
# join(), detach() and joinable() functions

Once a thread is created, we wait for it to complete execution by calling the `join()` function. Double join will result in program termination/ undefined behavior. Hence before joining, we should check if the thread is joinable using the joinable() method which returns true if the thread is joinable, false otherwise. Here is an example:

```c++
#include <iostream>
#include <chrono>
#include <thread>
using namespace std;

void run(int count) {
    while(count-- > 0) {
        cout << "C++Nuts" << endl;
        this_thread::sleep_for(chrono::seconds(5));
    }
}

int main() {
    thread t1(run, 10);
    t1.join();
    cout << "main() after" << endl;
    return 0;
}
```
Instead of joining directly, we should do it like this-

```c++
int main() {
    thread t1(run, 10);
    if(t1.joinable()){
        t1.join();
    }
    cout << "main() after" << endl;
    return 0;
}
```
Now if we wish to detach a thread from it's parent thread, we will call the `detach()` method. This will ensure the main thread does not wait for the thread to finish execution. Once a thread is detached, it will run freely on its own; the `std::thread` object ceases to have any association with the thread of execution and becomes non-joinable. It's the programmer's responsibility to ensure that the detached thread does not access any data that may go out of scope or become invalid during its execution. It is also the programmer's responsibility to ensure that the detached thread completes its work before the main program exits, or to implement some mechanism to ensure that the program does not exit prematurely, causing a crash.

Here is an example of how to use `detach()`:

```c++
#include <iostream>
#include <thread>

void worker() {
    // Do some work...
    std::cout << "Worker thread is executing." << std::endl;
}

int main() {
    std::thread t(worker);

    // Detach the thread and continue with main thread
    t.detach();

    if (t.joinable()) {
        // This won't be executed as the thread is detached and therefore not joinable
        t.join();
    }

    // The main program continues independently of the worker thread
    std::cout << "Main thread continues its execution." << std::endl;

    // The main thread should ensure that it outlives the worker thread
    // or implements a mechanism to keep the application running until
    // worker thread(s) complete their execution.
    
    return 0;
}
```

In this example, the main thread continues executing after detaching the worker thread. It is important to note that after detaching, you can't predict when the worker thread will execute. It might run concurrently with the main thread or afterwards, depending on the system's scheduling.

Important: Either join() or detach() should be called on thread object, otherwise during thread object's destructor it will terminate the program. Because inside destructor it checks if thread is still joinable? if yes then it terminates the program.

# Mutex, Race Conditiion and Critical Section

Race condition is a situation where two or more threads/process happen to change a common data at the same time. If there is a race condition then we have to protect it and the protected section is called critical section/region. Mutex is short for mutual exclusion and is used to avoid race condition. We use lock(), unlock() on mutex to avoid race condition.

```c++
#include<mutex>
#include<thread>

using namespace std;

int amount=0;

std::mutex m;

void addAmount(){
    m.lock();
    amount++;//Critical Section
    m.unlock();
}

int main(){
    std::thread t1(addAmount);
    std::thread t2(addAmount);
    t1.join();
    t2.join();

    return 0;
}
```

# Types of Mutex and Locks

In C++, there are different types of mutexes and locks to cater to various needs and scenarios:

1. **std::mutex**: The most basic mutex type. It provides exclusive, non-recursive ownership.
2. **std::recursive_mutex**: Allows the same thread to acquire the mutex multiple times.
3. **std::timed_mutex**: Extends std::mutex, allowing for time-based locking.
4. **std::recursive_timed_mutex**: Combines features of recursive_mutex and timed_mutex.

Locks are used in conjunction with mutexes to manage locking and unlocking in a more exception-safe manner:

- **std::lock_guard**: Automatically locks the mutex when it's created and unlocks it when destroyed.
- **std::unique_lock**: More flexible than lock_guard. Can lock and unlock mutexes multiple times.
- **std::scoped_lock (since C++17)**: Automatically locks and unlocks multiple mutexes without deadlock.

# Condition Variables

Condition variables are synchronization primitives used to block a thread or multiple threads until a particular condition is met. They require a mutex to lock the shared data and a predicate that defines the condition to wait for.

```c++
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>

std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void print_id(int id) {
    std::unique_lock<std::mutex> lock(mtx);
    while (!ready) {
        cv.wait(lock);
    }
    std::cout << "Thread " << id << '\n';
}

void go() {
    std::unique_lock<std::mutex> lock(mtx);
    ready = true;
    cv.notify_all();
}

int main() {
    std::thread threads[10];
    for (int i = 0; i < 10; ++i)
        threads[i] = std::thread(print_id, i);

    std::cout << "10 threads ready to race...\n";
    go();

    for (auto &th : threads) th.join();

    return 0;
}
```

# Thread Synchronization and Producer-Consumer Problem

Thread synchronization is crucial in multi-threaded applications to ensure that only one thread accesses a critical section of code at a time. This is achieved using mutexes, locks, and condition variables as described above.

The producer-consumer problem is a classic example of a multi-process synchronization problem. The problem describes two processes, the producer and the consumer, who share a common, fixed-size buffer as a queue. The producer’s job is to generate data, put it into the buffer, and start again. At the same time, the consumer is consuming the data (i.e., removing it from the buffer), one piece at a time.

Here's a simple implementation using C++:

```c++
#include <iostream>
#include <thread>
#include <queue>
#include <mutex>
#include <condition_variable>

std::mutex mtx;
std::condition_variable cv;
std::queue<int> products;

void producer(int id) {
    for (int i = 0; i < 5; ++i) {
        std::unique_lock<std::mutex> lock(mtx);
        std::cout << "Producer " << id << " produced " << i << std::endl;
        products.push(i);
        cv.notify_one(); // Notify consumer
        lock.unlock();
    }
}

void consumer(int id) {
    while (true) {
        std::unique_lock<std::mutex> lock(mtx);
        while (products.empty()) {
            cv.wait(lock); // Wait for a product
        }
        int product = products.front();
        products.pop();
        std::cout << "Consumer " << id << " consumed " << product << std::endl;
        lock.unlock();
    }
}

int main() {
    std::thread prod1(producer, 1);
    std::thread cons1(consumer, 1);
    std::thread cons2(consumer, 2);

    prod1.join();
    cons1.detach();
    cons2.detach();

    return 0;
}
```

This example showcases the basic principle of the producer-consumer problem, where synchronization tools like mutexes and condition variables are used to ensure safe and efficient data sharing between threads.