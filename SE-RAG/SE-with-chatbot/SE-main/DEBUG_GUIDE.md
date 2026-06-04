# Rider Name Sync - Debug Guide

## Problem
Rider name is not appearing on buyer's order tracking/detail screens after a rider accepts a delivery.

## Code Implementation Summary

### 1. Data Model ✅
- **File**: [lib/models/rider_assignment.dart](lib/models/rider_assignment.dart)
- **Changes**: Added `riderName` and `riderEmail` optional String fields
- **Status**: Fields are defined and serialization (toJson/fromJson) is implemented

### 2. Write Path (Rider accepts order) ✅
- **File**: [lib/providers/rider_provider.dart](lib/providers/rider_provider.dart#L73-L130)
- **Method**: `acceptDelivery()`
- **Process**:
  1. Fetches current rider's user document from Firestore
  2. Extracts displayName/email
  3. Writes to riderAssignments with payload:
     ```
     {
       'status': 'accepted',
       'acceptedAt': FieldValue.serverTimestamp(),
       'riderName': <rider name>,
       'riderEmail': <rider email>,
       'updatedAt': FieldValue.serverTimestamp()
     }
     ```
  4. **Enhanced Debugging**: Now logs all details before/after write, catches FirebaseExceptions with full error details

### 3. Firestore Security Rules ✅
- **File**: [firestore.rules](firestore.rules#L130-L140)
- **Update rule**: Allows riders to update their own assignments with these fields:
  - status, acceptedAt, pickedUpAt, deliveredAt
  - notes, earnings, riderName, riderEmail, updatedAt
- **Read rule**: Buyers can read assignments for their orders (orderOwnerUserId check)

### 4. Read Path (Buyer views order) ✅
- **File 1**: [lib/screens/orders/order_tracking_screen.dart](lib/screens/orders/order_tracking_screen.dart#L117-L180)
- **File 2**: [lib/screens/orders/order_detail_screen.dart](lib/screens/orders/order_detail_screen.dart#L522-L585)
- **Implementation**: StreamBuilder that:
  1. Listens to real-time snapshots of riderAssignments for the order
  2. Filters by status = accepted/pickedup/intransit/delivered
  3. Displays riderName and riderEmail if present
- **Enhanced Debugging**: Now logs all stream states and assignment data before filtering

## Debugging Steps

### Step 1: Check Console Logs (When Rider Accepts)
When a rider accepts a delivery, look for this log pattern in Flutter console:
```
═══════════════════════════════════════════════════════════════
🔵 ACCEPTING DELIVERY - DETAILED LOG:
  assignmentId: <ID>
  assignment.riderId: <RIDER_ID>
  currentUid: <CURRENT_UID>
  riderName: <NAME>
  riderEmail: <EMAIL>
  payload: {status: accepted, ...}
═══════════════════════════════════════════════════════════════
✅ Delivery accepted successfully: <ID>
```

**If you see `❌ FIRESTORE EXCEPTION`**:
- The write is failing - check the error code and message
- Likely issue: Firestore rules or permissions
- Solution: Verify rule syntax and that riderId in assignment matches currentUid

### Step 2: Check Buyer's Console (When Viewing Order)
When buyer opens order tracking/detail screen, look for:
```
═══════════════════════════════════════════════════════════════
🔵 ORDER TRACKING - RIDER INFO STREAM:
  orderId: <ORDER_ID>
  connectionState: active
  hasData: true
  docs.length: 1
  assignment data: {status: accepted, riderName: Wilmark, riderEmail: rider@test.com, ...}
═══════════════════════════════════════════════════════════════
```

**If `docs.length: 0`**:
- No assignment found for this order
- Check if orderId in the assignment matches the order being viewed

**If `riderName` is missing from assignment data**:
- Write may have failed silently
- Or write succeeded but without riderName field
- Check Step 1 logs for write errors

### Step 3: Verify Firestore Manually
Open Firebase Console → Firestore → riderAssignments collection:
1. Find the assignment doc for your test order
2. Check if these fields exist and have values:
   - `riderName` (should be e.g., "Wilmark")
   - `riderEmail` (should be e.g., "rider@test.com")
   - `status` (should be "accepted")

If fields are missing → write is being rejected by Firestore rules

## Test Scenario
1. **Rider Account**: rider@test.com / password
   - Accept a pending delivery order
   - Watch console for "ACCEPTING DELIVERY" logs
   
2. **Buyer Account**: kaehedarakazuha07@gmail.com / password
   - Open order details/tracking for the same order
   - Watch console for "RIDER INFO STREAM" logs
   - Check if rider name is displayed

## Common Issues & Fixes

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| Write succeeds (✅ log) but no data appears on buyer view | Read permission denied | Check orderOwnerUserId is correct in assignment |
| FirebaseException on write | Rule validation failed | Verify all fields in payload are in rule's hasOnly() list |
| riderName shows "Assigned Rider" (default) | Field not written | Check Firestore manually for presence of riderName |
| No rider section appears at all | Status filter blocking it | Ensure status in assignment is exactly "accepted" (not "Accepted") |

## Next Steps
1. Run the app and perform the test scenario above
2. Share console logs showing both "ACCEPTING DELIVERY" and "RIDER INFO STREAM" outputs
3. Compare what's being written vs. what's being read
4. Check Firestore console to confirm data was persisted

