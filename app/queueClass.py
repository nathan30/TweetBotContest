class Queue:

    #Constructor creates a list
    def __init__(self):
        self.queue = list()

    #Adding elements to queue
    def put(self,data):
        #Checking to avoid duplicate entry (not mandatory)
        if data not in self.queue:
            self.queue.insert(0,data)
            return True
        return False

    #Removing the last element from the queue
    def get(self):
        if len(self.queue)>0:
            return self.queue.pop()
        return False

    #Getting the size of the queue
    def empty(self):
        if len(self.queue) == 0:
            return True
        return False

    #printing the elements of the queue
    def printQueue(self):
        return self.queue

    def qsize(self):
        return len(self.queue)
