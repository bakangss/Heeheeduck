import multiprocessing

count = 0 

def smile_detection(thread_name):
    global count

    for x in range(10):
        count +=1
        print (thread_name,count)

    return count    

x = multiprocessing.Process(target=smile_detection, args=("Thread1",))
y = multiprocessing.Process(target=smile_detection, args=("Thread2",))
x.start()
y.start()