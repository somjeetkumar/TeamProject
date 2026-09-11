import http from "k6/http";
import { check, fail } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:8000/api";

const suffix = `${Date.now()}`;

const owner = {
    username: `smoke_owner_${suffix}`,
    email: `smoke_owner_${suffix}@example.com`,
    password: "Test@12345",
    password2: "Test@12345",
};

const member = {
    username: `smoke_member_${suffix}`,
    email: `smoke_member_${suffix}@example.com`,
    password: "Test@12345",
    password2: "Test@12345",
};

export const options = {
    vus: 1,
    iterations: 1,
};

function headers(token = null) {
    const h = {
        "Content-Type": "application/json",
    };

    if (token) {
        h.Authorization = `Bearer ${token}`;
    }

    return { headers: h };
}

function test(response, expectedStatus, name) {
    const passed = check(response, {
        [`${name} - status ${expectedStatus}`]:
            (r) => r.status === expectedStatus,
    });

    if (!passed) {
        console.error(`\n❌ ${name}`);
        console.error(`Status: ${response.status}`);
        console.error(`Response: ${response.body}\n`);
        fail(`${name} failed`);
    }

    console.log(`✓ ${name}`);
}

function getJSON(response) {
    try {
        return response.json();
    } catch (error) {
        fail(`Invalid JSON response: ${response.body}`);
    }
}

export default function () {

    console.log("\n==============================");
    console.log("   TASKFLOW SMOKE TEST");
    console.log("==============================\n");

    // =========================================================
    // 1. REGISTER OWNER
    // =========================================================

    let response = http.post(
        `${BASE_URL}/register/`,
        JSON.stringify(owner),
        headers()
    );

    test(response, 201, "Register owner");


    // =========================================================
    // 2. LOGIN OWNER
    // =========================================================

    response = http.post(
        `${BASE_URL}/login/`,
        JSON.stringify({
            username: owner.username,
            password: owner.password,
        }),
        headers()
    );

    test(response, 200, "Login owner");

    let data = getJSON(response);

    const accessToken = data.access;
    const refreshToken = data.refresh;

    check(response, {
        "Access token received": () => !!accessToken,
        "Refresh token received": () => !!refreshToken,
    });


    // =========================================================
    // 3. UNAUTHENTICATED REQUEST
    // =========================================================

    response = http.get(
        `${BASE_URL}/organizations/`
    );

    test(response, 401, "Unauthenticated request rejected");


    // =========================================================
    // 4. CREATE ORGANIZATION
    // =========================================================

    response = http.post(
        `${BASE_URL}/organizations/`,
        JSON.stringify({
            name: `Smoke Organization ${suffix}`,
        }),
        headers(accessToken)
    );

    test(response, 201, "Create organization");

    data = getJSON(response);

    const organizationId = data.id;


    // =========================================================
    // 5. LIST ORGANIZATIONS
    // =========================================================

    response = http.get(
        `${BASE_URL}/organizations/`,
        headers(accessToken)
    );

    test(response, 200, "List organizations");


    // =========================================================
    // 6. GET ORGANIZATION
    // =========================================================

    response = http.get(
        `${BASE_URL}/organizations/${organizationId}/`,
        headers(accessToken)
    );

    test(response, 200, "Get organization");


    // =========================================================
    // 7. CREATE TEAM
    // =========================================================

    response = http.post(
        `${BASE_URL}/organizations/${organizationId}/teams/`,
        JSON.stringify({
            name: `Smoke Team ${suffix}`,
        }),
        headers(accessToken)
    );

    test(response, 201, "Create team");

    data = getJSON(response);

    const teamId = data.id;


    // =========================================================
    // 8. LIST TEAMS
    // =========================================================

    response = http.get(
        `${BASE_URL}/organizations/${organizationId}/teams/`,
        headers(accessToken)
    );

    test(response, 200, "List teams");


    // =========================================================
    // 9. GET TEAM
    // =========================================================

    response = http.get(
        `${BASE_URL}/teams/${teamId}/`,
        headers(accessToken)
    );

    test(response, 200, "Get team");


    // =========================================================
    // 10. REGISTER MEMBER
    // =========================================================

    response = http.post(
        `${BASE_URL}/register/`,
        JSON.stringify(member),
        headers()
    );

    test(response, 201, "Register member");

    data = getJSON(response);

    const memberId = data.user.id;


    // =========================================================
    // 11. ADD MEMBER TO ORGANIZATION
    // =========================================================

    response = http.post(
        `${BASE_URL}/organizations/${organizationId}/members/`,
        JSON.stringify({
            user: memberId,
            role: "member",
        }),
        headers(accessToken)
    );

    test(response, 201, "Add organization member");

    data = getJSON(response);

    const organizationMembershipId = data.id;


    // =========================================================
    // 12. LIST ORGANIZATION MEMBERS
    // =========================================================

    response = http.get(
        `${BASE_URL}/organizations/${organizationId}/members/`,
        headers(accessToken)
    );

    test(response, 200, "List organization members");


    // =========================================================
    // 13. ADD MEMBER TO TEAM
    // =========================================================

    response = http.post(
        `${BASE_URL}/teams/${teamId}/members/`,
        JSON.stringify({
            user: memberId,
        }),
        headers(accessToken)
    );

    test(response, 201, "Add team member");

    data = getJSON(response);

    const teamMembershipId = data.id;


    // =========================================================
    // 14. LIST TEAM MEMBERS
    // =========================================================

    response = http.get(
        `${BASE_URL}/teams/${teamId}/members/`,
        headers(accessToken)
    );

    test(response, 200, "List team members");


    // =========================================================
    // 15. CREATE PROJECT + TASK
    // =========================================================

    response = http.post(
        `${BASE_URL}/projects/`,
        JSON.stringify({
            name: `Smoke Project ${suffix}`,
            description: "Smoke test project",
            team: teamId,

            task: {
                title: `Smoke Initial Task ${suffix}`,
                description: "Smoke test task",
                status: "todo",
                priority: "medium",
                assignee: memberId,
            },
        }),
        headers(accessToken)
    );

    test(response, 201, "Create project with nested task");

    data = getJSON(response);

    const projectId = data.id;


    // =========================================================
    // 16. LIST PROJECTS
    // =========================================================

    response = http.get(
        `${BASE_URL}/projects/`,
        headers(accessToken)
    );

    test(response, 200, "List projects");


    // =========================================================
    // 17. GET PROJECT
    // =========================================================

    response = http.get(
        `${BASE_URL}/projects/${projectId}/`,
        headers(accessToken)
    );

    test(response, 200, "Get project");


    // =========================================================
    // 18. CREATE TASK
    // =========================================================

    response = http.post(
        `${BASE_URL}/tasks/`,
        JSON.stringify({
            project: projectId,
            title: `Smoke Task ${suffix}`,
            description: "Smoke test task",
            status: "todo",
            priority: "high",
            assignee: memberId,
        }),
        headers(accessToken)
    );

    test(response, 201, "Create task");

    data = getJSON(response);

    const taskId = data.id;


    // =========================================================
    // 19. GET TASK
    // =========================================================

    response = http.get(
        `${BASE_URL}/tasks/${taskId}/`,
        headers(accessToken)
    );

    test(response, 200, "Get task");


    // =========================================================
    // 20. LIST TASKS + PAGINATION
    // =========================================================

    response = http.get(
        `${BASE_URL}/tasks/?page=1&page_size=10`,
        headers(accessToken)
    );

    test(response, 200, "List tasks with pagination");

    data = getJSON(response);

    check(data, {
        "Task pagination has results":
            (d) => Array.isArray(d.results),

        "Task pagination has count":
            (d) => d.count !== undefined,
    });


    // =========================================================
    // 21. UPDATE TASK
    // =========================================================

    response = http.put(
        `${BASE_URL}/tasks/${taskId}/`,
        JSON.stringify({
            project: projectId,
            title: `Smoke Task Updated ${suffix}`,
            description: "Updated by smoke test",
            status: "in_progress",
            priority: "high",
            assignee: memberId,
        }),
        headers(accessToken)
    );

    test(response, 200, "Update task");


    // =========================================================
    // 22. CREATE COMMENT
    // =========================================================

    response = http.post(
        `${BASE_URL}/tasks/${taskId}/comments/`,
        JSON.stringify({
            content: "Smoke test comment",
        }),
        headers(accessToken)
    );

    test(response, 201, "Create comment");

    data = getJSON(response);

    const commentId = data.id;


    // =========================================================
    // 23. LIST COMMENTS + PAGINATION
    // =========================================================

    response = http.get(
        `${BASE_URL}/tasks/${taskId}/comments/?page=1&page_size=10`,
        headers(accessToken)
    );

    test(response, 200, "List comments with pagination");

    data = getJSON(response);

    check(data, {
        "Comment pagination has results":
            (d) => Array.isArray(d.results),

        "Comment pagination has count":
            (d) => d.count !== undefined,
    });


    // =========================================================
    // 24. UPDATE COMMENT
    // =========================================================

    response = http.put(
        `${BASE_URL}/comments/${commentId}/`,
        JSON.stringify({
            content: "Updated smoke test comment",
        }),
        headers(accessToken)
    );

    test(response, 200, "Update comment");


    // =========================================================
    // 25. REFRESH TOKEN
    // =========================================================

    response = http.post(
        `${BASE_URL}/token/refresh/`,
        JSON.stringify({
            refresh: refreshToken,
        }),
        headers()
    );

    test(response, 200, "Refresh token");


    // =========================================================
    // CLEANUP
    // =========================================================

    response = http.del(
        `${BASE_URL}/comments/${commentId}/`,
        null,
        headers(accessToken)
    );

    test(response, 204, "Delete comment");


    response = http.del(
        `${BASE_URL}/tasks/${taskId}/`,
        null,
        headers(accessToken)
    );

    test(response, 204, "Delete task");


    response = http.del(
        `${BASE_URL}/team-members/${teamMembershipId}/`,
        null,
        headers(accessToken)
    );

    test(response, 204, "Delete team membership");


    response = http.del(
        `${BASE_URL}/organization-members/${organizationMembershipId}/`,
        null,
        headers(accessToken)
    );

    test(response, 204, "Delete organization membership");


    response = http.del(
        `${BASE_URL}/projects/${projectId}/`,
        null,
        headers(accessToken)
    );

    test(response, 204, "Delete project");


    response = http.del(
        `${BASE_URL}/teams/${teamId}/`,
        null,
        headers(accessToken)
    );

    test(response, 204, "Delete team");


    response = http.del(
        `${BASE_URL}/organizations/${organizationId}/`,
        null,
        headers(accessToken)
    );

    test(response, 204, "Delete organization");


//     // =========================================================
//     // LOGOUT
//     // =========================================================

//     response = http.post(
//         `${BASE_URL}/logout/`,
//         JSON.stringify({
//             refresh: refreshToken,
//         }),
//         headers(accessToken)
//     );

//     test(response, 200, "Logout");


//     console.log("\n================================");
//     console.log("     SMOKE TEST PASSED");
//     console.log("================================\n");
}




// // k6 run -e BASE_URL=http://127.0.0.1:8000/ smoke-test/smoketest.js 