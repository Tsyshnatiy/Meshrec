#include "off_exporter.h"

int main(int ac, char* av[])
{
  if (ac < 3)
  {
    throw std::invalid_argument("Not enough arguments for the app");
  }

  std::string from(av[1]);
  std::string to(av[2]);

  OffExporter exporter(from, to);
  exporter.convert();
  return 0;
}

