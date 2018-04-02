#include "off_exporter.h"

#include <iostream>

#include <SketchUpAPI/initialize.h>
#include <SketchUpAPI/model/entity.h>
#include <SketchUpAPI/model/face.h>
#include <SketchUpAPI/model/model.h>
#include <SketchUpAPI/model/vertex.h>
#include <SketchUpAPI/model/entities.h>
#include <SketchUpAPI/model/mesh_helper.h>
#include <SketchUpAPI/model/group.h>
#include <SketchUpAPI/model/component_definition.h>
#include <SketchUpAPI/model/component_instance.h>
#include <SketchUpAPI/model/geometry.h>

#include "utils.h"

namespace
{
	double idx(const SUTransformation& tr, int i, int j)
	{
		return tr.values[i * 4 + j];
	}

	double& idxRef(SUTransformation& tr, int i, int j)
	{
		return tr.values[i * 4 + j];
	}

  SUTransformation identityMatrix()
  {
    SUTransformation result;
    std::vector<int> v = { 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1 };
    std::copy(v.begin(), v.end(), result.values);

    return result;
  }

  void fillRow(SUTransformation& r, const SUTransformation& t1, const SUTransformation& t2, int row)
  {
    for (int j = 0; j < 4; ++j)
    {
      idxRef(r, row, j) = idx(t1, row, 0) * idx(t2, 0, j) + idx(t1, row, 1) * idx(t2, 1, j)
        + idx(t1, row, 2) * idx(t2, 2, j) + idx(t1, row, 3) * idx(t2, 3, j);
    }
  }

  SUTransformation multiply(const SUTransformation& t1, const SUTransformation& t2)
  {
    SUTransformation r;

    for (int i = 0; i < 4; ++i)
    {
      fillRow(r, t1, t2, i);
    }

    return r;
  }

  void applyTransformation(std::vector<SUPoint3D>& vertices, const SUTransformation& transformation)
  {
    for (auto& vert : vertices)
    {
      SU_CALL(SUPoint3DTransform(&transformation, &vert));
    }
  }
}

OffExporter::OffExporter(const std::string& src, const std::string& dst)
  : file(dst)
  , sourceFilePath(src)
{
  meshTriangles.reserve(4096);
  SUSetInvalid(model);
}

OffExporter::~OffExporter()
{
  releaseModelObjects();
}

void OffExporter::releaseModelObjects() {
  if (!SUIsInvalid(model)) {
    SUModelRelease(&model);
    SUSetInvalid(model);
  }

  // Terminate the SDK
  SUTerminate();
}

bool OffExporter::convert()
{
  bool exported = false;
  try
  {
    // Initialize the SDK
    SUInitialize();

    // Create the model from the src_file
    SUSetInvalid(model);
    SU_CALL(SUModelCreateFromFile(&model, sourceFilePath.c_str()));

    if (!file.open())
    {
      throw std::invalid_argument("Unable to open file " + file.name());
    }

    file.writeHeader();

    writeGeometry();

    exported = true;
  }
  catch (const std::exception& e)
  {
    std::cout << ("Error while processing: " + std::string(e.what())) << std::endl;
    exported = false;
  }

  return exported;
}

void OffExporter::updateIndices()
{
  for (auto& pair : ptIndexMap)
  {
    pair.second = idxGen.get();
  }
}

void OffExporter::writeGeometry()
{
  SUEntitiesRef model_entities;
  SU_CALL(SUModelGetEntities(model, &model_entities));

  collectTrianglesAndVertices(model_entities, identityMatrix());

  // Update indices when full map is created
  updateIndices();

  file.writeVertsFacesEdges(ptIndexMap.size(), meshTriangles.size(), 0);
  file.writeVertices(ptIndexMap);
  file.writeTriangles(meshTriangles, ptIndexMap);
}

void OffExporter::collectTrianglesAndVertices(SUEntitiesRef entities, const SUTransformation& transformation)
{
  // Component instances
  size_t num_instances = 0;
  SU_CALL(SUEntitiesGetNumInstances(entities, &num_instances));
  if (num_instances > 0)
  {
    std::vector<SUComponentInstanceRef> instances(num_instances);
    SU_CALL(SUEntitiesGetInstances(entities, num_instances,
      &instances[0], &num_instances));
    for (size_t c = 0; c < num_instances; c++)
    {
      SUComponentInstanceRef instance = instances[c];
      SUComponentDefinitionRef definition = SU_INVALID;
      SU_CALL(SUComponentInstanceGetDefinition(instance, &definition));

	    SUTransformation componentTransform;
	    SUComponentInstanceGetTransform(instance, &componentTransform);

	    auto tr = multiply(componentTransform, transformation);

      SUEntitiesRef componentEntities;
      SUComponentDefinitionGetEntities(definition, &componentEntities);

      collectTrianglesAndVertices(componentEntities, tr);
    }
  }

  size_t num_groups = 0;
  SU_CALL(SUEntitiesGetNumGroups(entities, &num_groups));
  if (num_groups > 0)
  {
    std::vector<SUGroupRef> groups(num_groups);
    SU_CALL(SUEntitiesGetGroups(entities, num_groups, &groups[0], &num_groups));
    for (size_t g = 0; g < num_groups; g++)
    {
      SUGroupRef group = groups[g];
      SUEntitiesRef group_entities = SU_INVALID;
      SU_CALL(SUGroupGetEntities(group, &group_entities));

      SUTransformation groupTransform;
      SU_CALL(SUGroupGetTransform(group, &groupTransform));

	    auto tr = multiply(groupTransform, transformation);

      collectTrianglesAndVertices(group_entities, tr);
    }
  }

  auto faces = extractFaces(entities);

  if (faces.size() != 0)
  {
    collectTrianglesAndVerticesFromFaces(faces, transformation);
  }
}

std::vector<SUFaceRef> OffExporter::extractFaces(SUEntitiesRef entities)
{
  size_t num_faces = 0;
  SU_CALL(SUEntitiesGetNumFaces(entities, &num_faces));
  if (num_faces == 0)
  {
    return std::vector<SUFaceRef>();
  }

  std::vector<SUFaceRef> result(num_faces);
  SU_CALL(SUEntitiesGetFaces(entities, num_faces, &result[0], &num_faces));
  return result;
}

void OffExporter::collectTrianglesAndVerticesFromFaces(const std::vector<SUFaceRef>& faces, const SUTransformation& transformation)
{
  for (size_t i = 0; i < faces.size(); i++)
  {
    computeTrianglesAndVerticesFromFace(faces[i], transformation);
  }
}

void OffExporter::computeTrianglesAndVerticesFromFace(SUFaceRef face, const SUTransformation& transformation)
{
  size_t num_triangles = 0;

  SUMeshHelperRef mesh_ref = SU_INVALID;
  SU_CALL(SUMeshHelperCreate(&mesh_ref, face));
  SU_CALL(SUMeshHelperGetNumTriangles(mesh_ref, &num_triangles));

  // Get the vertices
  size_t num_vertices = 0;
  SU_CALL(SUMeshHelperGetNumVertices(mesh_ref, &num_vertices));
  if (num_vertices == 0)
    return;

  std::vector<SUPoint3D> vertices(num_vertices);
  SU_CALL(SUMeshHelperGetVertices(mesh_ref, num_vertices, &vertices[0], &num_vertices));

  applyTransformation(vertices, transformation);

  // Get triangle indices.
  SU_CALL(SUMeshHelperGetNumTriangles(mesh_ref, &num_triangles));

  const size_t num_indices = 3 * num_triangles;
  size_t num_retrieved = 0;
  std::vector<size_t> indices(num_indices);
  SU_CALL(SUMeshHelperGetVertexIndices(mesh_ref, num_indices, &indices[0], &num_retrieved));

  for (size_t i_triangle = 0; i_triangle < num_triangles; i_triangle++)
  {
    Triangle triangle;
    for (size_t i = 0; i < 3; i++)
    {
      // Get vertex
      size_t index = indices[i_triangle * 3 + i];
      triangle.pts[i].SetLocation(vertices[index].x, vertices[index].y, vertices[index].z);

      auto it = ptIndexMap.find(triangle.pts[i]);
      if (it == ptIndexMap.end())
      {
        ptIndexMap.emplace(triangle.pts[i], 0);
      }
    }

    meshTriangles.push_back(triangle);
  }
}