

# **A Technical Primer on Implementing a Nanite-Inspired Virtualized Geometry System**

## **Introduction**

For decades, real-time 3D graphics have been governed by a strict set of budgets. Artists and engineers have been locked in a perpetual struggle against the limitations of polygon counts, draw call overhead, and finite graphics memory.1 This paradigm forced the creation of complex and often creatively stifling asset production pipelines. Highly detailed source assets, such as film-quality sculpts or photogrammetry scans, could not be used directly. Instead, they had to be manually simplified into low-polygon models, with the lost detail painstakingly baked into normal maps—a process that consumes significant artist time and can introduce visual artifacts.2 This traditional approach meant that a scene's performance was fundamentally tied to its geometric complexity; more triangles meant more processing, leading to a hard cap on visual fidelity.

The advent of virtualized geometry systems, most notably Unreal Engine's Nanite, represents a fundamental paradigm shift in rendering technology. These systems break the direct link between scene complexity and performance, re-casting the primary performance metric from triangle count to the number of pixels on the screen.4 The core principle of virtualized geometry is to treat geometric data akin to virtual memory or virtual textures: the full, high-fidelity source asset resides on disk, and only the microscopic detail that is perceptible to the viewer in any given frame is streamed into active memory and rendered.6 This approach not only liberates artists to work directly with cinematic-quality assets but also enables the creation of scenes with geometric detail orders of magnitude greater than what was previously possible in real-time.3

This report serves as a detailed technical primer for developers seeking to understand and implement the core logic of a Nanite-inspired virtualized geometry system. It deconstructs the system into its primary architectural pillars, providing a logical roadmap for implementation. The focus is not on a specific API or code, but on the underlying algorithms and data structures that make such a system work. The key components that will be explored are:

1. **A Specialized Data Format:** An offline pre-processing stage that converts standard meshes into a hierarchical structure of triangle clusters, optimized for GPU processing and streaming.  
2. **A GPU-Driven Rendering Pipeline:** A runtime architecture that offloads visibility determination, culling, and Level of Detail (LOD) selection from the CPU to the GPU, enabling massive scalability.  
3. **An On-Demand Streaming Subsystem:** A data management system that dynamically moves geometry from storage to VRAM, ensuring that only the necessary data resides in memory at any time.

By understanding these core principles, a technically proficient indie team can begin to chart a course toward implementing their own virtualized geometry engine, unlocking a new frontier of visual fidelity.

## **Section 1: The Foundational Data Structure: Offline Asset Conditioning**

The power of a virtualized geometry system does not begin at runtime; it begins with a sophisticated offline pre-processing pipeline. This crucial asset conditioning step transforms a standard, high-polygon mesh into a purpose-built data structure that is highly compressed and optimized for the unique demands of the GPU-driven runtime. This one-time conversion process is the foundation upon which the entire system is built.

### **1.1 From Meshes to Meshlets: The Logic of Geometry Partitioning**

The first and most fundamental step in asset conditioning is to decompose a monolithic, arbitrarily complex mesh into a large number of small, uniformly sized, and topologically simple groups of triangles. These groups are commonly referred to as "clusters" or "meshlets".7 In Unreal's Nanite, these clusters are defined as containing a maximum of 128 triangles.7

The primary motivation behind this partitioning is to transform a heterogeneous rendering problem into a homogeneous one. GPUs are massively parallel processors that achieve their performance through a Single Instruction, Multiple Threads (SIMT) execution model, which is most efficient when performing the same operation on large, uniform batches of data.13 A single, complex mesh with intricate topology does not map well to this model. However, by breaking it down into thousands of simple, fixed-size clusters, the geometry workload becomes a vast array of identical tasks. This allows for the design of compute shaders where a single GPU workgroup can be dispatched to process exactly one cluster. This perfect mapping of the data structure to the GPU's compute architecture is the key to the system's efficiency and scalability. It is not merely a strategy for culling; it is a fundamental re-architecting of the geometry processing problem to be GPU-native.

For a practical implementation, developers can leverage existing open-source libraries. While graph partitioning libraries like METIS can be used 12, the most direct and widely adopted tool is the

meshoptimizer library by Arseny Kapoulkine. This library is referenced in numerous open-source virtual geometry implementations and provides highly optimized functions for generating meshlets from standard mesh data.14 The output of this stage is a flat list of meshlets. Each meshlet contains its own small, self-contained index buffer (using "micro-indices" that refer only to vertices within that meshlet) and a list of the unique vertices it uses. This ensures each cluster is an independent, processable unit, ready for the next stages of the pipeline.

### **1.2 Building the Hierarchy: A Deep Dive into Mesh Simplification**

After the base mesh has been partitioned into its finest-level clusters (LOD 0), the system must generate the coarser levels of detail. This is achieved by recursively grouping adjacent clusters and simplifying them to create a new parent cluster that represents the same surface area with fewer triangles.18 This process is repeated, building a hierarchy of LODs from the most detailed base layer upwards.

The simplification process is guided by a geometric error metric, which quantifies the visual deviation of the simplified mesh from the original surface. The most common and effective technique for this is the Quadric Error Metric (QEM), a well-established algorithm from academic computer graphics that is highly effective at preserving the shape and volume of the original mesh during simplification.19 The simplification itself is typically performed through a series of iterative edge collapse operations, where two vertices along an edge are merged into one, thereby removing the triangles that shared that edge.19 Foundational concepts for view-dependent refinement and the use of error metrics can be found in the literature for algorithms like Real-time Optimally Adapting Meshes (ROAM).1

A critical and complex challenge during this stage is ensuring that the resulting LODs can be seamlessly stitched together at runtime without producing visible cracks or holes. When two adjacent clusters are rendered at different LODs, their shared boundary must match perfectly. This requires constraining the edge collapse operations at the borders of cluster groups. The simplification of a boundary edge must be deterministic and dependent only on the vertices of that edge, so that both adjacent cluster groups arrive at the exact same simplified representation for their shared border, regardless of the simplification happening within the interior of each group. This guarantees watertight transitions at runtime.

### **1.3 The Cluster Graph: A Directed Acyclic Graph for Continuous LOD**

The resulting hierarchical structure is not a simple tree, but a more flexible Directed Acyclic Graph (DAG).7 This distinction is subtle but significant. In a simple tree, each node has exactly one parent. In a DAG, a node can have multiple parents.

This structure is employed because it allows for more efficient data representation and more optimal simplification pathways. A group of, for instance, four child clusters might be simplified together to form one parent. However, a different, overlapping group of four clusters might also be simplified to form another parent. A DAG structure allows a child cluster group to be shared by these multiple potential parents. This gives the runtime LOD selection algorithm far more flexibility to find an optimal "cut" through the graph—a selection of clusters from various LODs—that best represents the mesh for a given viewpoint while minimizing error and maintaining seamless connectivity.

The final data structure can be visualized with the original 128-triangle clusters as the leaf nodes of the graph. Each non-leaf (parent) node contains its own simplified geometry data, pointers to its children, and a stored value representing the geometric error introduced by its simplification. This error value is paramount for the runtime LOD selection logic.

### **1.4 Data Encoding and Compression for Efficient Streaming**

The final step of the offline conditioning process is to take the entire cluster DAG and all associated vertex data and serialize it into a highly compressed binary format. The goal is to minimize both the on-disk footprint and the amount of data that needs to be transferred from disk to VRAM during on-demand streaming.6

This involves a variety of data reduction techniques. Vertex attributes like positions, normals, and texture coordinates are quantized to lower-precision formats (e.g., 16-bit floats or normalized integers) to save space.16 The connectivity data itself (the micro-indices within each meshlet) can be encoded using specialized techniques like generalized triangle strips, which improve on standard triangle lists by reusing vertices more efficiently.25 The vertex data within each cluster can also be encoded relative to the cluster's bounding box, further reducing the number of bits required.

The output of this entire offline pipeline is a single, compact binary asset file for each source mesh. This file contains the fully compressed and organized cluster DAG, ready to be efficiently parsed and streamed by the runtime engine.

## **Section 2: The Runtime Core: A GPU-Driven Rendering Pipeline**

With the assets pre-processed into an optimized format, the focus shifts to the per-frame runtime logic. The core of a Nanite-like system is a fully GPU-driven rendering pipeline, which fundamentally changes the division of labor between the CPU and GPU to achieve unprecedented scalability.

### **2.1 Paradigm Shift: From CPU-Bound to GPU-Driven**

In a traditional rendering pipeline, the CPU is the master orchestrator. Each frame, it traverses the scene graph, determines which objects are potentially visible (frustum culling), sorts them by material, and then issues a distinct draw call to the GPU for each object or batch of objects.28 This process makes the CPU a significant bottleneck; the performance is limited by the number of draw calls it can issue and the complexity of the scene graph it must process.

In a GPU-driven pipeline, this relationship is inverted. The CPU's role is minimized. At the start of a frame, it may upload a small amount of data for dynamic objects whose transforms have changed, but its primary job is to launch a handful of compute shaders.7 These compute shaders then take over the entire process of visibility determination, culling, and LOD selection directly on the GPU. The GPU effectively "feeds itself" with rendering commands, processing the entire scene in a few large, highly parallel dispatches.30 This architectural shift leverages the massive parallelism of the GPU to perform work that was previously a serial bottleneck on the CPU, enabling the system to handle scenes with millions of instances and billions of triangles.29

### **2.2 The Culling Cascade: Identifying Visible Geometry**

To efficiently render scenes of immense complexity, the system must aggressively cull geometry that will not contribute to the final image. This is performed on the GPU through a multi-stage cascade that rejects the vast majority of geometry before any expensive rasterization or shading occurs.

Stage 1: Instance Culling  
The first pass is a compute shader that operates on the level of entire object instances. Each thread in the dispatch can be assigned to a single instance in the scene. It performs two primary checks:

* **Frustum Culling:** A standard test to see if the instance's bounding box intersects with the camera's view frustum.  
* **Occlusion Culling:** A more advanced test to see if the instance is hidden behind other objects that are closer to the camera. This is accomplished with extreme efficiency by testing the instance's bounding box against a **Hierarchical Z-Buffer (HZB)**.7 The HZB is a mipmapped version of the previous frame's depth buffer. Each successively smaller mip level stores the furthest depth value from the 2x2 block of pixels in the level above it. This structure allows the GPU to test the bounding box of an object against the depth of a large screen area with just a few texture fetches from the appropriate HZB mip level, making the occlusion test extremely fast.32

Stage 2: Cluster Culling  
For each instance that survives the first culling stage, a second compute shader pass is launched to perform culling at a much finer granularity: the individual cluster level.7 Each cluster within the surviving instances has its own pre-computed bounding sphere or box. This pass repeats the frustum and HZB occlusion tests for every single cluster.  
The power of this two-pass, hierarchical approach cannot be overstated. While HZB-based occlusion is a known technique, applying it at the cluster level is what makes it revolutionary for virtualized geometry. Frame-to-frame coherence in typical gameplay is very high, meaning the depth buffer from the previous frame is an excellent predictor of visibility for the current frame.32 By testing potentially millions of tiny cluster bounding boxes against the HZB, the GPU can cheaply and rapidly determine that, for example, 95% of a mountain that is behind another mountain is occluded, and only pass the visible peak clusters to the next stage. This fine-grained, intra-object occlusion is impossible to achieve with traditional per-object occlusion queries, which suffer from high latency and can stall the pipeline.35

### **2.3 Dynamic LOD Selection: Traversing the Cluster Graph**

The clusters that survive the culling cascade represent the set of potentially visible geometry at the highest level of detail. The next step is to select the appropriate LOD for each of these clusters based on their visibility to the camera. This is the core of the automated, continuous LOD system.

A compute shader is dispatched to process the list of visible leaf clusters. For each cluster, the shader evaluates a screen-space error metric. A simple and effective metric is to calculate the projected size of the cluster's bounding sphere on the screen. If this projected size is smaller than a target threshold—for example, a single pixel—the cluster is deemed a candidate for simplification.5

The shader then traverses the cluster DAG *upwards* from the leaf nodes.18 If a cluster and all of its sibling clusters (i.e., all children of a single parent node in the DAG) are visible and all are determined to be smaller than the error threshold, the system can replace that entire group of child clusters with their single, simplified parent cluster. This process is repeated recursively up the graph. The shader is effectively finding the highest-level (coarsest) "cut" through the DAG that still meets the desired visual fidelity, ensuring that no more detail is rendered than is necessary. The output of this stage is the final, optimized list of clusters, drawn from many different levels of the LOD hierarchy, that will be rasterized for the current frame.

### **2.4 The Visibility Buffer: A Modern Approach to Deferred Geometry**

Rather than immediately shading the final list of selected clusters, modern GPU-driven pipelines introduce an intermediate step that uses a **Visibility Buffer** (sometimes called an ID buffer).11 This is a crucial step that completely decouples the process of determining geometry visibility from the process of calculating material properties and lighting.

The pipeline performs a "visibility-only" pass where the selected clusters are rasterized into a special render target. This is not a standard color or G-Buffer target. It is typically a 64-bit integer buffer where, for each pixel, the system stores a compact, unique identifier for the geometry that is visible at that pixel. This 64-bit value is often packed with 32 bits for the depth value and 32 bits for an ID that combines the instance ID, the cluster ID, and the specific triangle ID within that cluster.31 As multiple triangles may cover the same pixel, visibility is resolved using atomic operations in the pixel or compute shader (e.g., an

atomicMax operation on the 64-bit integer, where depth is stored in the most significant bits). This allows the GPU to correctly determine the closest triangle for each pixel in a massively parallel way without pipeline stalls or ordering dependencies.36

The result is a complete, screen-space map of "what is visible where." This visibility buffer now serves as a lookup table for all subsequent shading passes, which no longer need to know anything about the original geometry or the culling process.37

**Table 1: Comparison of Rendering Paradigms**

| Feature | Traditional CPU-Driven Pipeline | GPU-Driven Virtualized Geometry Pipeline |
| :---- | :---- | :---- |
| **Primary Bottleneck** | CPU: Draw calls, state changes, scene graph traversal 1 | GPU: Pixel shading, screen resolution 5 |
| **Geometry Granularity** | Per-Object or per-material batches 28 | Per-Cluster (e.g., 128 triangles) 7 |
| **Culling & LOD** | Coarse-grained, CPU-based frustum/occlusion culling; manual, discrete LODs 4 | Fine-grained, GPU-based culling (HZB); automatic, continuous LOD selection 7 |
| **Artist Workflow** | Manual LOD creation, normal map baking, polygon budget management 2 | Direct import of high-poly source assets; budgets are largely eliminated 4 |
| **Scalability** | Limited by object and triangle counts in the scene 1 | Limited by the number of pixels on screen; scales to billions of triangles 5 |

## **Section 3: Rasterization and Shading Logic**

Once the visibility buffer has been populated, the pipeline knows precisely which triangle is visible at every pixel. The final stage is to use this information to rasterize the geometry and apply the correct material shading to produce the final image. This involves a hybrid rasterization strategy and a highly evolved, GPU-driven material pipeline.

### **3.1 A Hybrid Rasterization Strategy**

A key challenge in rendering scenes with potentially pixel-sized detail is the performance characteristics of hardware rasterizers. Standard GPU hardware is highly optimized for processing medium-to-large triangles that cover many pixels. However, when triangles become smaller than a pixel (a state referred to as micropolygon rendering), performance can degrade significantly. This is due to the "pixel-quad" problem: GPUs process pixels in 2x2 blocks for efficiency, particularly for calculating texture coordinate derivatives. If a tiny triangle only touches one pixel within that 2x2 quad, the computational resources for the other three pixels are largely wasted, leading to poor hardware utilization.31

To overcome this, a virtualized geometry system employs a hybrid rasterization strategy, dynamically choosing the best approach on a per-cluster basis.7

* **Hardware Rasterization Path:** For clusters that are close to the camera, their triangles will be large and cover many pixels. In this case, the system utilizes the GPU's fast, fixed-function hardware rasterizer, which is the most efficient option for this type of workload.  
* **Software Rasterization Path:** For clusters that are far from the camera, their triangles will be very small, often smaller than a single pixel. For these, the system switches to a custom "software rasterizer" implemented entirely within a compute shader.11 This software rasterizer is highly specialized for this micropolygon use case. It can process many tiny triangles in parallel, calculating coverage and writing depth and ID information directly to the visibility buffer using atomic operations, bypassing the overhead and inefficiencies of the fixed-function hardware pipeline for this specific workload.

The decision of which path to use for a given cluster is made during the LOD selection phase, based on the cluster's predicted screen-space size. Open-source projects like nanite-webgpu provide a valuable reference for implementing a software rasterizer, even with the constraints of web APIs.24 Academic projects such as Micropolis also explore the concepts of micropolygon rendering in detail.40

### **3.2 The GPU-Driven Material Pipeline**

With the visibility buffer fully populated, the renderer has all the information needed to shade the scene. For each pixel, it knows the precise instance, cluster, and triangle, and by extension, the material that should be applied. The challenge is performing this shading efficiently. A naive approach of dispatching a separate full-screen draw call for every visible material would be highly inefficient due to state changes and overdraw, where each pixel is tested against every material.37

The modern, highly optimized solution is a multi-pass compute-based approach often called **Shade Binning**, as detailed in GDC 2024 presentations on Nanite's material pipeline.36 This process classifies and groups pixels by material before shading them.

1. **Count Pass:** A compute shader is dispatched that launches one thread per 2x2 pixel region. Each thread reads the visibility buffer, determines the material ID for the pixels in its region, and uses atomic operations to increment a global counter for each unique material ID encountered. This pass efficiently builds a histogram of how many pixels on screen belong to each material.  
2. **Reserve and Scatter Passes:** This is effectively a GPU-based counting sort. A "reserve" pass reads the material counts and allocates contiguous blocks of memory in a single large buffer for each visible material. A "scatter" pass then re-reads the visibility buffer and writes the screen coordinates of each pixel into the appropriate "bin" within that large buffer. The result is a tightly packed list of all pixels that need to be shaded with Material A, followed by a list for Material B, and so on. Memory locality is critical here; pixels are often processed in 8x8 tiles and Morton-ordered to improve cache performance during the scatter.36  
3. **Shading Dispatch:** Finally, a separate compute shader dispatch is launched for each *visible* material bin. Each thread in this dispatch is responsible for a single pixel. It reads a pixel coordinate from its assigned bin, uses the IDs from the visibility buffer to look up the full vertex attributes (position, normals, UVs) from the global geometry buffers, executes the corresponding material's shader graph, and writes the final G-Buffer values (e.g., Base Color, Roughness, World Normal) using UAV writes.

A significant optimization in this GPU-driven model addresses the "empty draw problem." Since the CPU dispatches the initial passes, it doesn't know which of the thousands of potential materials in a project will actually be visible in a given frame. A naive implementation would require the CPU to issue a dispatch command for every single material, even if 99% of them have zero visible pixels. These "empty dispatches" create significant overhead on the GPU's command processor.36 Modern graphics APIs provide a solution. With DirectX 12's

**Work Graphs** or similar vendor-specific extensions, the CPU can launch a single "entry node".41 This entry node runs the Count Pass on the GPU. Then, critically, the GPU itself can read the resulting count buffer and dynamically launch the subsequent shading work

*only for the material bins with a count greater than zero*. This entire process of checking for work and launching subsequent tasks happens on the GPU without returning to the CPU, eliminating the empty dispatch overhead and dramatically improving performance.

## **Section 4: Virtualized Geometry: The Streaming Subsystem**

The final core component is the streaming subsystem, which embodies the "virtualized" aspect of the technology. This system is responsible for managing the flow of geometric data from slower, high-capacity storage (like an SSD) to fast, limited-capacity VRAM, ensuring that the renderer has access to the data it needs precisely when it needs it.

### **4.1 Principles of On-Demand Data Streaming**

The fundamental assumption of a virtualized geometry system is that the full, high-resolution geometric data for an entire game level or scene is far too large to fit into VRAM at once.6 To manage this, the compressed geometry data generated during the offline conditioning process is stored on disk and divided into discrete chunks, or

**pages**.

The runtime operates on a principle of on-demand, fine-grained streaming. This concept is directly analogous to virtual texturing, but applied to mesh data instead of pixel data.6 The renderer maintains a cache of geometry pages in VRAM. When the rendering process requires a cluster whose data page is not currently in the VRAM cache (a "cache miss"), a request is generated to load that page from disk. This entire system is predicated on the ability to rapidly stream data, making a Solid State Drive (SSD) a practical hardware requirement for achieving smooth, hitch-free performance.6

### **4.2 The Streaming Manager: Logic and Heuristics**

The streaming process is orchestrated by a feedback loop between the GPU and a CPU-side Streaming Manager.

* **GPU Feedback Loop:** During the runtime culling and LOD selection passes, if a compute shader determines that a specific cluster is needed for rendering but its corresponding data page is not currently resident in VRAM, it does not stall. Instead, it records the ID of the required page into a special **feedback buffer** on the GPU.  
* **CPU Streaming Manager:** Each frame, a dedicated thread on the CPU reads this feedback buffer. This Streaming Manager is responsible for the high-level logic of the streaming system. Its primary tasks are:  
  1. **Issue Load Requests:** For each unique page ID in the feedback buffer, the manager issues an asynchronous read request to the storage device.  
  2. **Manage VRAM Cache:** It maintains an in-memory pool of allocated VRAM pages, tracking which pages are in use, free, or pending a load.  
  3. **Prioritize Requests:** Not all requests are equal. The manager must prioritize loads based on importance. A common heuristic is to prioritize pages associated with clusters that have a larger predicted screen-space error. A high-detail cluster needed for a foreground object is more important than a low-detail cluster for a distant object.  
  4. **Evict Old Data:** To make room for new pages, the manager must evict pages from the VRAM cache. A simple Least Recently Used (LRU) policy is a common and effective strategy.

A proposal for a streaming system in the Godot engine outlines a simplified but practical version of this logic, which serves as a good conceptual starting point for an indie implementation. It involves defining fixed-size pages and using the GPU culling results to drive streaming requests in a similar feedback loop.45

### **4.3 Hardware Enablers: The Role of Direct Memory Access (DMA)**

To prevent the CPU from becoming a bottleneck in the data transfer process itself, modern systems rely heavily on Direct Memory Access (DMA). DMA is a hardware feature that allows the GPU to pull data directly from system storage (or main memory) into its own VRAM with minimal intervention from the CPU.9 The CPU simply initiates the transfer request, and a dedicated DMA controller handles the data movement, freeing the CPU to work on other tasks like game logic or physics.

Modern storage APIs, such as Microsoft's **DirectStorage** and similar technologies on consoles, are the high-level software interfaces that expose this hardware capability to developers. These APIs are designed specifically for the high-throughput, parallel I/O patterns required by game streaming systems and are a key enabler for achieving the performance necessary for virtualized geometry.

## **Section 5: A Practical Roadmap for Implementation**

Implementing a full-featured virtualized geometry system is a monumental undertaking, likely beyond the scope of a small indie team if approached as a single, monolithic task.46 However, by breaking the problem down into a series of logical, iterative phases and by leveraging the powerful open-source ecosystem, it becomes a more manageable, albeit still ambitious, goal.

### **5.1 A Phased Approach to Implementation**

A pragmatic approach is to build the system in discrete, testable stages, with each phase adding a new layer of core functionality. This allows for incremental progress and ensures that a functional, if simplified, system exists at every step.

**Table 2: Phased Implementation Roadmap**

| Phase | Core Goal | Key Components to Implement | Recommended Tools/APIs | Success Metric |
| :---- | :---- | :---- | :---- | :---- |
| **1: Meshlet Rendering** | Render a single, static high-poly mesh efficiently. | Offline meshlet generation. GPU pipeline to load all meshlets and render with a single indirect draw call. | meshoptimizer, DrawIndexedIndirect | A high-poly model renders at interactive framerates, proving the core data format and batching works. |
| **2: GPU Culling** | Efficiently render a scene with many instances of high-poly meshes. | GPU-based frustum culling. Implement Hierarchical Z-Buffer (HZB) generation and occlusion culling. | Compute Shaders, Atomic Counters | Framerate remains high when looking away from the scene or when major occluders are present. |
| **3: Hierarchical LOD** | Render a single, massive object with seamless, continuous LOD. | Extend offline tool to build the full cluster DAG with error metrics. Implement runtime DAG traversal and screen-space error evaluation. | Quadric Error Metrics (QEM) | A single, complex object (e.g., a detailed statue) maintains high detail up close and simplifies smoothly in the distance without visible popping. |
| **4: Virtualized Streaming** | Render a scene whose geometric data exceeds available VRAM. | Page-based asset format. GPU feedback buffer for page requests. CPU-side streaming manager with caching and eviction logic. | Asynchronous File I/O, DirectStorage (if available) | The engine can navigate a massive environment without crashing due to VRAM exhaustion, with acceptable or minimal stuttering. |
| **5: Advanced Shading** | Implement a fully decoupled and highly efficient material pipeline. | Visibility Buffer pass. Material classification and shade binning via compute shaders. (Optional) Software rasterizer for micropolygons. | Compute Shaders, Atomic Operations, Work Graphs (if available) | Complex scenes with many different materials render efficiently, and performance scales with resolution rather than material complexity. |

### **5.2 Leveraging the Open-Source Ecosystem**

No developer should attempt this in a vacuum. The graphics programming community has produced a wealth of tools and reference implementations that are invaluable for understanding and building these complex systems.

* **Essential Tools:** The meshoptimizer library is a non-negotiable starting point. It provides robust, industry-tested algorithms for meshlet generation, simplification, and optimization that would take immense effort to replicate.15  
* **Case Studies:** Studying existing open-source projects is crucial for learning. The goal is not to copy code, but to understand how the theoretical concepts are translated into practical solutions.  
  * **nanite-webgpu:** This project is an excellent, self-contained reference. It demonstrates the meshlet hierarchy, GPU culling, and even a software rasterizer, all within the understandable constraints of the WebGPU API. It is a perfect starting point for dissecting the core rendering loop.24  
  * **Bevy's Virtual Geometry:** The work being done in the Bevy engine shows how these concepts can be integrated into a larger, more complete game engine framework. The public design discussions on their GitHub provide invaluable, real-world insights into the design trade-offs, challenges, and architectural decisions involved.18  
  * **NVIDIA and AMD Samples:** Both GPU vendors provide official samples demonstrating the use of their latest hardware features, such as mesh shaders and work graphs. These are essential for understanding how to use the low-level APIs required to implement the most advanced and performant parts of the pipeline, such as the GPU-driven material system.43

### **5.3 Key Challenges and Potential Simplifications**

It is vital to be realistic about the scope of this project. A 1:1 clone of a production-grade system like Nanite is the result of many years of work by a large team of expert engineers. An indie developer must make pragmatic simplifications to deliver a functional system.

* **Skip the Software Rasterizer (Initially):** Rely entirely on the hardware rasterizer. This is far simpler to implement and will work well for a wide range of content. Accept the performance penalty for micropolygons as a reasonable trade-off for reduced complexity.  
* **Simplify the Material Pipeline:** Instead of a full compute-based shade binning system, start with the approach used in the initial version of Nanite: render one full-screen pass per visible material, using the GPU's hardware depth test (with depth-equals) to mask out pixels that don't belong to that material.36 This is significantly easier to implement and still provides a massive improvement over traditional forward rendering.  
* **Simplify Streaming:** A full, fine-grained, cluster-level streaming system is complex. A good initial step is to implement a coarser, object-level streaming system. Entire objects can be loaded or unloaded based on their distance from the camera. This solves the problem of VRAM exhaustion for large open worlds, paving the way for a more granular system later.

## **Conclusion**

The architecture of a Nanite-inspired virtualized geometry system represents a profound evolution in real-time rendering. By shifting the computational burden from the CPU to the GPU and rethinking how geometric data is structured, processed, and rendered, it enables a level of visual fidelity and scale previously confined to offline, cinematic productions. The core architectural pillars of this paradigm are clear and built upon decades of graphics research:

1. **Offline Data Conditioning:** Transforming standard meshes into a compressed, hierarchical **Cluster DAG**, making geometry a first-class citizen for GPU computation.  
2. **A GPU-Driven Pipeline:** Leveraging compute shaders for a fine-grained **culling and LOD cascade** that populates a **Visibility Buffer**, effectively decoupling geometry processing from material shading.  
3. **Hybrid Rasterization and Shading:** Using a combination of hardware and software rasterization to handle triangles of all sizes, and employing a fully decoupled, compute-based material pipeline for maximum efficiency.  
4. **On-Demand Streaming:** Implementing a **virtual memory system for geometry**, ensuring that only the data currently needed resides in VRAM.

While the engineering challenge of building such a system from the ground up is significant, it is not insurmountable. The principles are now well-documented in academic papers, conference presentations, and open-source projects. By adopting a phased implementation strategy, leveraging essential open-source tools like meshoptimizer, and making pragmatic simplifications where necessary, a technically-minded indie developer or small team can successfully build a custom virtualized geometry engine. The result is the ability to create game worlds of breathtaking complexity and detail, finally breaking free from the polygon budgets of the past.

#### **Works cited**

1. Journey to Nanite \- High Performance Graphics, accessed June 27, 2025, [https://www.highperformancegraphics.org/slides22/Journey\_to\_Nanite.pdf](https://www.highperformancegraphics.org/slides22/Journey_to_Nanite.pdf)  
2. SIGGRAPH Unreal 5 A Deep Dive into Nanite Virtualized Geometry : r/pcgaming \- Reddit, accessed June 27, 2025, [https://www.reddit.com/r/pcgaming/comments/qjmckv/siggraph\_unreal\_5\_a\_deep\_dive\_into\_nanite/](https://www.reddit.com/r/pcgaming/comments/qjmckv/siggraph_unreal_5_a_deep_dive_into_nanite/)  
3. What is virtualized micropolygon geometry? An explainer on Nanite | Unreal Engine 5, accessed June 27, 2025, [https://www.youtube.com/watch?v=-50MJf7hyOw](https://www.youtube.com/watch?v=-50MJf7hyOw)  
4. Unreal Engine 5 and Nanite virtualized geometry \- Magnopus, accessed June 27, 2025, [https://www.magnopus.com/blog/unreal-engine-5-and-nanite-virtualized-geometry](https://www.magnopus.com/blog/unreal-engine-5-and-nanite-virtualized-geometry)  
5. Nanite for Educators and Students \- Unreal Engine, accessed June 27, 2025, [https://cdn2.unrealengine.com/nanite-for-educators-and-students-2-b01ced77f058.pdf](https://cdn2.unrealengine.com/nanite-for-educators-and-students-2-b01ced77f058.pdf)  
6. Nanite Virtualized Geometry in Unreal Engine \- Epic Games Developers, accessed June 27, 2025, [https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-virtualized-geometry-in-unreal-engine)  
7. How does Unreal Engine 5's Nanite work? \- Game Development ..., accessed June 27, 2025, [https://gamedev.stackexchange.com/questions/198454/how-does-unreal-engine-5s-nanite-work](https://gamedev.stackexchange.com/questions/198454/how-does-unreal-engine-5s-nanite-work)  
8. Nanite \- Advances in Real-Time Rendering in 3D Graphics and Games, accessed June 27, 2025, [https://advances.realtimerendering.com/s2021/Karis\_Nanite\_SIGGRAPH\_Advances\_2021\_final.pdf](https://advances.realtimerendering.com/s2021/Karis_Nanite_SIGGRAPH_Advances_2021_final.pdf)  
9. Nanite, a revolution for virtualized geometry with Unreal Engine 5 \- SkyReal, accessed June 27, 2025, [https://skyreal.tech/news/nanite-a-revolution-for-virtualized-geometry-with-unreal-engine-5/](https://skyreal.tech/news/nanite-a-revolution-for-virtualized-geometry-with-unreal-engine-5/)  
10. Basics of Nanites in Unreal Engine 5 | by Logan Hochwald | Medium, accessed June 27, 2025, [https://medium.com/@loganhochwald/basics-of-nanites-in-unreal-engine-5-ac4ad7c434f1](https://medium.com/@loganhochwald/basics-of-nanites-in-unreal-engine-5-ac4ad7c434f1)  
11. How does the nanite feature of unreal engine 5 work? : r/howdidtheycodeit \- Reddit, accessed June 27, 2025, [https://www.reddit.com/r/howdidtheycodeit/comments/pg9hld/how\_does\_the\_nanite\_feature\_of\_unreal\_engine\_5/](https://www.reddit.com/r/howdidtheycodeit/comments/pg9hld/how_does_the_nanite_feature_of_unreal_engine_5/)  
12. Geometry Processing \- LMU München \- Medieninformatik, accessed June 27, 2025, [https://www.medien.ifi.lmu.de/lehre/ws2122/gp/slides/gp-ws2122-extra-nanite.pdf](https://www.medien.ifi.lmu.de/lehre/ws2122/gp/slides/gp-ws2122-extra-nanite.pdf)  
13. Optimize GPU Workloads for Graphics Applications with NVIDIA Nsight Graphics, accessed June 27, 2025, [https://resources.nvidia.com/en-us-nsight-developer-tools/optimize-gpu-workload](https://resources.nvidia.com/en-us-nsight-developer-tools/optimize-gpu-workload)  
14. Oh, nice. Third party implementations of Nanite playback. Nanite is a very cleve... | Hacker News, accessed June 27, 2025, [https://news.ycombinator.com/item?id=41459509](https://news.ycombinator.com/item?id=41459509)  
15. Mesh Shaders and Meshlet Culling in Metal 3, accessed June 27, 2025, [https://metalbyexample.com/mesh-shaders/](https://metalbyexample.com/mesh-shaders/)  
16. Optimizing Graphics Pipelines with Meshlets: A Guide to Efficient Geometry Processing, accessed June 27, 2025, [https://www.packtpub.com/en-us/learning/how-to-tutorials/optimizing-graphics-pipelines-with-meshlets-a-guide-to-efficient-geometry-processing](https://www.packtpub.com/en-us/learning/how-to-tutorials/optimizing-graphics-pipelines-with-meshlets-a-guide-to-efficient-geometry-processing)  
17. zeux/meshoptimizer: Mesh optimization library that makes ... \- GitHub, accessed June 27, 2025, [https://github.com/zeux/meshoptimizer](https://github.com/zeux/meshoptimizer)  
18. Virtual Geometry in Bevy 0.14 \- JMS55, accessed June 27, 2025, [https://jms55.github.io/posts/2024-06-09-virtual-geometry-bevy-0-14/](https://jms55.github.io/posts/2024-06-09-virtual-geometry-bevy-0-14/)  
19. Efficient Implementation of Real-Time View-Dependent ... \- IFI UZH, accessed June 27, 2025, [https://www.ifi.uzh.ch/dam/jcr:ffffffff-82b7-d340-ffff-ffffa65fb649/FastMeshIEEE.pdf](https://www.ifi.uzh.ch/dam/jcr:ffffffff-82b7-d340-ffff-ffffa65fb649/FastMeshIEEE.pdf)  
20. A Real-time System of Crowd Rendering: Parallel LOD and Texture-Preserving Approach on GPU \- People, accessed June 27, 2025, [https://people.cs.vt.edu/yongcao/publication/pdf/chao2011\_MIG.pdf](https://people.cs.vt.edu/yongcao/publication/pdf/chao2011_MIG.pdf)  
21. Appearance-Driven Automatic 3D Model Simplification, accessed June 27, 2025, [https://users.aalto.fi/\~laines9/publications/hasselgren2021egsr\_paper.pdf](https://users.aalto.fi/~laines9/publications/hasselgren2021egsr_paper.pdf)  
22. Dynamic multiresolution level of detail mesh simplification for real ..., accessed June 27, 2025, [https://www.researchgate.net/publication/4167554\_Dynamic\_multiresolution\_level\_of\_detail\_mesh\_simplification\_for\_real-time\_rendering\_of\_large\_digital\_terrain\_models](https://www.researchgate.net/publication/4167554_Dynamic_multiresolution_level_of_detail_mesh_simplification_for_real-time_rendering_of_large_digital_terrain_models)  
23. Aokana: A GPU-Driven Voxel Rendering Framework for Open World Games \- ResearchGate, accessed June 27, 2025, [https://www.researchgate.net/publication/392803107\_Aokana\_A\_GPU-Driven\_Voxel\_Rendering\_Framework\_for\_Open\_World\_Games](https://www.researchgate.net/publication/392803107_Aokana_A_GPU-Driven_Voxel_Rendering_Framework_for_Open_World_Games)  
24. Scthe/nanite-webgpu: UE5's Nanite implementation using ... \- GitHub, accessed June 27, 2025, [https://github.com/Scthe/nanite-webgpu](https://github.com/Scthe/nanite-webgpu)  
25. Optimized Geometry Compression for Real-time Rendering \- DSpace@MIT, accessed June 27, 2025, [http://dspace.mit.edu/bitstream/handle/1721.1/44895/41227273-MIT.pdf?sequence=2](http://dspace.mit.edu/bitstream/handle/1721.1/44895/41227273-MIT.pdf?sequence=2)  
26. Efficient Geometry Compression for GPU-Based Decoding in Realtime Terrain Rendering \- Department of Computer Science, accessed June 27, 2025, [https://www.cs.cit.tum.de/fileadmin/w00cfj/cg/Research/Publications/2009/Efficient\_Geometry\_Compression/CGF09.pdf](https://www.cs.cit.tum.de/fileadmin/w00cfj/cg/Research/Publications/2009/Efficient_Geometry_Compression/CGF09.pdf)  
27. Efficient Geometry Compression for GPU-based Decoding in Realtime Terrain Rendering | Request PDF \- ResearchGate, accessed June 27, 2025, [https://www.researchgate.net/publication/220506786\_Efficient\_Geometry\_Compression\_for\_GPU-based\_Decoding\_in\_Realtime\_Terrain\_Rendering](https://www.researchgate.net/publication/220506786_Efficient_Geometry_Compression_for_GPU-based_Decoding_in_Realtime_Terrain_Rendering)  
28. opengl \- What is GPU driven rendering? \- Stack Overflow, accessed June 27, 2025, [https://stackoverflow.com/questions/59686151/what-is-gpu-driven-rendering](https://stackoverflow.com/questions/59686151/what-is-gpu-driven-rendering)  
29. GPU Driven Rendering Overview \- Vulkan Guide, accessed June 27, 2025, [https://vkguide.dev/docs/gpudriven/gpu\_driven\_engines/](https://vkguide.dev/docs/gpudriven/gpu_driven_engines/)  
30. GPU Driven Rendering and Virtual Texturing in Trials Rising Oleksandr Drazhevskyi Technical Lead Ubisoft Kiev \- GDC Vault, accessed June 27, 2025, [https://media.gdcvault.com/gdc2019/presentations/Drazhevskyi\_Oleksandr\_GPU\_Driven\_Rendering.pdf](https://media.gdcvault.com/gdc2019/presentations/Drazhevskyi_Oleksandr_GPU_Driven_Rendering.pdf)  
31. Analysis of UE5 Rendering Technology: Nanite \- Habr, accessed June 27, 2025, [https://habr.com/en/articles/655105/](https://habr.com/en/articles/655105/)  
32. GPU-Driven Clustered Forward Renderer | Hacker News, accessed June 27, 2025, [https://news.ycombinator.com/item?id=44043045](https://news.ycombinator.com/item?id=44043045)  
33. GPU Driven Occlusion Culling in Life is Feudal, accessed June 27, 2025, [https://bazhenovc.github.io/blog/post/gpu-driven-occlusion-culling-slides-lif/](https://bazhenovc.github.io/blog/post/gpu-driven-occlusion-culling-slides-lif/)  
34. GPU-driven rendering (SIGGRAPH 2015 follow up) \- Beyond3D Forum, accessed June 27, 2025, [https://forum.beyond3d.com/threads/gpu-driven-rendering-siggraph-2015-follow-up.57240/](https://forum.beyond3d.com/threads/gpu-driven-rendering-siggraph-2015-follow-up.57240/)  
35. Chapter 29\. Efficient Occlusion Culling \- NVIDIA Developer, accessed June 27, 2025, [https://developer.nvidia.com/gpugems/gpugems/part-v-performance-and-practicalities/chapter-29-efficient-occlusion-culling](https://developer.nvidia.com/gpugems/gpugems/part-v-performance-and-practicalities/chapter-29-efficient-occlusion-culling)  
36. Nanite GPU Driven Materials \- GDC Vault, accessed June 27, 2025, [https://media.gdcvault.com/gdc2024/Slides/GDC+slide+presentations/Nanite+GPU+Driven+Materials.pdf](https://media.gdcvault.com/gdc2024/Slides/GDC+slide+presentations/Nanite+GPU+Driven+Materials.pdf)  
37. A Deep Dive into Nanite Virtualized Geometry \- YouTube, accessed June 27, 2025, [https://www.youtube.com/watch?v=eviSykqSUUw](https://www.youtube.com/watch?v=eviSykqSUUw)  
38. HPG 2022 Keynote: The Journey to Nanite \- Brian Karis, Epic Games \- YouTube, accessed June 27, 2025, [https://www.youtube.com/watch?v=NRnj\_lnpORU](https://www.youtube.com/watch?v=NRnj_lnpORU)  
39. Why do GPUs not have HW triangle optimized Rasterization : r/computergraphics \- Reddit, accessed June 27, 2025, [https://www.reddit.com/r/computergraphics/comments/1jy7qyk/why\_do\_gpus\_not\_have\_hw\_triangle\_optimized/](https://www.reddit.com/r/computergraphics/comments/1jy7qyk/why_do_gpus_not_have_hw_triangle_optimized/)  
40. ginkgo/micropolis: A micropolygon rasterizer written in OpenCL \- GitHub, accessed June 27, 2025, [https://github.com/ginkgo/micropolis](https://github.com/ginkgo/micropolis)  
41. Advancing GPU-Driven Rendering with Work Graphs in Direct3D 12 \- NVIDIA Developer, accessed June 27, 2025, [https://developer.nvidia.com/blog/advancing-gpu-driven-rendering-with-work-graphs-in-direct3d-12/](https://developer.nvidia.com/blog/advancing-gpu-driven-rendering-with-work-graphs-in-direct3d-12/)  
42. Advanced Graphics Summit: GPU Work Graphs: Towards GPU-Driven Games | Schedule 2025 | Game Developers Conference (GDC), accessed June 27, 2025, [https://schedule.gdconf.com/session/advanced-graphics-summit-gpu-work-graphs-towards-gpu-driven-games/909736](https://schedule.gdconf.com/session/advanced-graphics-summit-gpu-work-graphs-towards-gpu-driven-games/909736)  
43. GDC 2024 Work graphs and draw calls – a match made in heaven\! \- AMD GPUOpen, accessed June 27, 2025, [https://gpuopen.com/learn/gdc-2024-workgraphs-drawcalls/](https://gpuopen.com/learn/gdc-2024-workgraphs-drawcalls/)  
44. Game-on-demand: An online game engine based on geometry streaming \- ResearchGate, accessed June 27, 2025, [https://www.researchgate.net/publication/220214518\_Game-on-demand\_An\_online\_game\_engine\_based\_on\_geometry\_streaming](https://www.researchgate.net/publication/220214518_Game-on-demand_An_online_game_engine_based_on_geometry_streaming)  
45. Implement Mesh streaming · Issue \#6109 · godotengine/godot-proposals \- GitHub, accessed June 27, 2025, [https://github.com/godotengine/godot-proposals/issues/6109](https://github.com/godotengine/godot-proposals/issues/6109)  
46. Discussion about Virtualized Geometry (as introduced by UE5's ..., accessed June 27, 2025, [https://github.com/bevyengine/bevy/discussions/10433](https://github.com/bevyengine/bevy/discussions/10433)  
47. NVIDIA RTX Mega Geometry Now Available with New Vulkan Samples, accessed June 27, 2025, [https://developer.nvidia.com/blog/nvidia-rtx-mega-geometry-now-available-with-new-vulkan-samples/](https://developer.nvidia.com/blog/nvidia-rtx-mega-geometry-now-available-with-new-vulkan-samples/)