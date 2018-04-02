#include "off_file.h"

#include <stdexcept>

OffFile::OffFile(const std::string& fname)
  : filename(fname)
{
}

OffFile::~OffFile()
{
  close();
}

bool OffFile::open()
{
  if (!fileStream.is_open())
  {
    fileStream.open(filename.c_str(), std::ofstream::out);

    if (!fileStream.is_open())
    {
      return false;
    }
  }
  
  return true;
}

void OffFile::close()
{
  if (fileStream.is_open())
  {
    fileStream.flush();
    fileStream.close();
  }
}

std::string OffFile::name() const
{ 
  return filename;
}

void OffFile::writeHeader()
{
  fileStream << header << std::endl;
}

void OffFile::writeVertsFacesEdges(size_t vertsNum, size_t facesNum, size_t edgesNum)
{
  fileStream << vertsNum << " " << facesNum << " " << edgesNum << std::endl;
}

void OffFile::writeVertices(const std::map<GeomUtils::CPoint3d, int>& vertices)
{
  for (const auto& vert : vertices)
  {
    fileStream << vert.first.x() << " " << vert.first.y() << " " << vert.first.z() << std::endl;
  }
}

void OffFile::writeTriangles(const std::vector<Triangle>& triangles, const std::map<GeomUtils::CPoint3d, int>& ptIndexMap)
{
  for (const auto& triangle : triangles)
  {
    int idx[3];
    for (int i = 0; i < 3; ++i)
    {
      auto it = ptIndexMap.find(triangle.pts[i]);

      if (it == ptIndexMap.end())
      {
        throw std::logic_error("Found additional point");
      }

      idx[i] = it->second;
    }

    fileStream << 3 << " " << idx[0] << " " << idx[1] << " " << idx[2] << std::endl;
  }
}