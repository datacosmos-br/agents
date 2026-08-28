#include <thread>

struct Buffer {
  char* data;
  Buffer() : data(new char[64]) {}
};

void increment(int* total) { ++*total; }

int run() {
  int total = 0;
  std::thread first(increment, &total);
  std::thread second(increment, &total);
  first.join();
  second.join();
  return total;
}
