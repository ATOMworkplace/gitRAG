import React, { useRef, useEffect, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { PointMaterial } from "@react-three/drei";

// Helper: More points near poles
function randomPolarPoint(r = 2.0, polarBias = 2.2) {
  // High polarBias puts more points near z axis (Earth poles)
  const theta = Math.acos(2 * Math.random() ** polarBias - 1);
  const phi = 2 * Math.PI * Math.random();
  return [
    r * Math.sin(theta) * Math.cos(phi),
    r * Math.sin(theta) * Math.sin(phi),
    r * Math.cos(theta)
  ];
}

// Spherical sinusoidal local orbit
function sphereWave([x0, y0, z0], t, i) {
  const r = Math.sqrt(x0 * x0 + y0 * y0 + z0 * z0);
  const theta0 = Math.atan2(Math.sqrt(x0 * x0 + y0 * y0), z0);
  const phi0 = Math.atan2(y0, x0);
  const phase = i * 0.21;
  const theta =
    theta0 +
    Math.sin(t * 0.37 + phase) * 0.13 +
    Math.cos(t * 0.16 + phase) * 0.11;
  const phi = phi0 + Math.sin(t * 0.21 + phase) * 0.15;
  return [
    r * Math.sin(theta) * Math.cos(phi),
    r * Math.sin(theta) * Math.sin(phi),
    r * Math.cos(theta)
  ];
}

function SpherePoints({
  pointCount = 5000,
  polarBias = 5,
  scatterStrength = 1.3,
  sphereRadius = 3
}) {
  const mesh = useRef();
  const [basePoints] = useState(() =>
    Array.from({ length: pointCount }).map((_, i) => [
      ...randomPolarPoint(sphereRadius, polarBias),
      i
    ])
  );
  const scatterOffsets = useRef(basePoints.map(() => [0, 0, 0]));
  const { camera, gl } = useThree();
  const mouseNDC = useRef([0, 0]);

  // Mouse move handler for scatter
  useEffect(() => {
    function handlePointerMove(e) {
      const rect = gl.domElement.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      mouseNDC.current = [x, y];
    }
    gl.domElement.addEventListener("pointermove", handlePointerMove);
    return () =>
      gl.domElement.removeEventListener("pointermove", handlePointerMove);
  }, [gl]);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const positions = mesh.current.geometry.attributes.position;
    for (let i = 0; i < basePoints.length; i++) {
      const [x0, y0, z0, index] = basePoints[i];
      const [fx, fy, fz] = sphereWave([x0, y0, z0], t, index);

      // Interactive scatter (repel from cursor)
      const vec = new THREE.Vector3(fx, fy, fz).project(camera);
      const dx = vec.x - mouseNDC.current[0];
      const dy = vec.y - mouseNDC.current[1];
      const d = Math.sqrt(dx * dx + dy * dy);

      let target = [0, 0, 0];
      let scatter = false;
      if (d < 0.21) {
        const s = ((0.21 - d) / 0.21) * scatterStrength;
        const len = Math.sqrt(fx * fx + fy * fy + fz * fz) || 1;
        target = [fx / len * s, fy / len * s, fz / len * s];
        scatter = true;
      }
      // Use fast lerp for scatter, slow lerp for return
      const lerp = scatter ? 0.17 : 0.045; // Fast when scattering, slow when returning!
      let [ox, oy, oz] = scatterOffsets.current[i];
      ox += (target[0] - ox) * lerp;
      oy += (target[1] - oy) * lerp;
      oz += (target[2] - oz) * lerp;
      scatterOffsets.current[i] = [ox, oy, oz];

      positions.setXYZ(i, fx + ox, fy + oy, fz + oz);
    }
    positions.needsUpdate = true;
  });

  return (
    <points ref={mesh}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={basePoints.length}
          array={new Float32Array(
            basePoints.map(([x, y, z]) => [x, y, z]).flat()
          )}
          itemSize={3}
        />
      </bufferGeometry>
      <PointMaterial
        color="#fff"
        size={0.04}
        sizeAttenuation
        transparent
        depthWrite={false}
      />
    </points>
  );
}

export default function PointCloudSphere() {
  return (
    <Canvas
      camera={{ position: [0, 0, 6] }}
      style={{ width: 480, height: 480, background: "transparent" }}
      gl={{ alpha: true }}
    >
      <ambientLight intensity={0.95} />
      <SpherePoints />
    </Canvas>
  );
}
