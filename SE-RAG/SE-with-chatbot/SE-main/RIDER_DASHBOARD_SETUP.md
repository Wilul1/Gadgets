
# Rider Dashboard Module Setup

## Overview
A complete rider delivery management system has been integrated into the TechHub app. Riders can now view assigned orders, accept/decline deliveries, update delivery status, and track earnings.

## Components Created

### 1. Data Models

#### `lib/models/rider_assignment.dart`
- **RiderDeliveryStatus enum**: assigned, accepted, declined, pickedUp, inTransit, delivered
- **RiderAssignment class**: Stores delivery assignment information
  - Fields: id, orderId, riderId, orderOwnerUserId, status, timestamps (assignedAt, acceptedAt, pickedUpAt, deliveredAt), earnings, notes
  - Methods: `statusText` getter, `copyWith()`, serialization (`toJson()`, `fromJson()`)

### 2. State Management

#### `lib/providers/rider_provider.dart`
- Manages rider assignments and delivery operations
- **Key methods**:
  - `loadRiderAssignments()`: Fetch rider's assignments from Firestore
  - `acceptDelivery(String assignmentId)`: Accept a delivery
  - `declineDelivery(String assignmentId, String reason)`: Decline with reason
  - `updateDeliveryStatus(String assignmentId, RiderDeliveryStatus newStatus)`: Update status (pickedUp, inTransit, delivered)
  - `clearAssignments()`: Clear data on logout
- **Getters**:
  - `assignedDeliveries`: Filter for 'assigned' status
  - `activeDeliveries`: Filter for accepted/pickedUp/inTransit
  - `completedDeliveries`: Filter for 'delivered' status
  - `totalEarnings`: Calculate earnings from completed deliveries

### 3. UI Screens

#### `lib/screens/rider/rider_dashboard_screen.dart`
- Main rider dashboard with tabbed interface
- **Tabs**:
  1. **Assigned**: Deliveries in 'assigned' status - shows Accept/Decline buttons
  2. **Active**: Deliveries being processed - shows status update buttons (Mark as Picked Up → In Transit → Delivered)
  3. **Completed**: Finished deliveries - shows delivery date and earnings
- **Earnings Card**: Displays total earnings, completed count, active count
- **Features**:
  - Pull-to-refresh on all tabs
  - Real-time status updates via RiderProvider
  - Decline confirmation dialog with reason input
  - Error handling with SnackBars

### 4. Models Updated

#### `lib/models/user.dart`
- Added `role` field (String?): Stores 'admin', 'rider', 'user', etc.
- Updated serialization methods: `toJson()`, `fromJson()`, `toFirestore()`, `fromFirestore()`
- Updated `copyWith()` to include role parameter

### 5. Auth Provider

#### `lib/providers/auth_provider.dart`
- Updated to load and store user role from Firestore
- Role set during registration: 'admin' for admin@techhub.com, 'user' for regular users
- Can be changed to 'rider' via admin or external tools

### 6. App Configuration

#### `lib/config/routes.dart`
- Added `riderDashboard` route constant
- Added route handler for `RiderDashboardScreen`

#### `lib/main.dart`
- Added `RiderProvider` to MultiProvider list
- Updated routing logic: If user role is 'rider', show `RiderDashboardScreen` instead of `MainScreen`
- Added imports for rider dashboard and provider

## Firestore Integration

### Collection: `riderAssignments`

#### Document Structure
```json
{
  "orderId": "order_123",
  "riderId": "rider_uid",
  "orderOwnerUserId": "buyer_uid",
  "status": "assigned|accepted|declined|pickedUp|inTransit|delivered",
  "assignedAt": Timestamp,
  "acceptedAt": Timestamp | null,
  "pickedUpAt": Timestamp | null,
  "deliveredAt": Timestamp | null,
  "earnings": 10.5,
  "notes": "Any notes from rider"
}
```

### Firestore Rules (Updated)

```javascript
match /riderAssignments/{assignmentId} {
  // Admins can read all assignments
  allow read: if isAdmin();
  
  // Riders can read only their own assignments
  allow read: if request.auth != null && resource.data.riderId == request.auth.uid;

  // Admins can create assignments for any order/rider
  allow create: if isAdmin()
    && request.resource.data.keys().hasAll(['orderId','riderId','orderOwnerUserId','status','assignedAt'])
    && request.resource.data.status == 'assigned';

  // Update:
  // - Admins can update any assignment
  // - Riders can only update their own assignments and only specific fields
  //   Riders CANNOT change: orderId, riderId, orderOwnerUserId
  allow update: if isAdmin()
    || (
      request.auth != null
      && request.auth.uid == resource.data.riderId
      && !('orderId' in request.resource.data)
      && !('riderId' in request.resource.data)
      && !('orderOwnerUserId' in request.resource.data)
      && request.resource.data.keys().hasOnly(resource.data.keys().union(['status','acceptedAt','pickedUpAt','deliveredAt','notes','earnings','updatedAt']))
    );

  // Delete:
  // - Admins can delete any assignment
  allow delete: if isAdmin();
}
```

## Usage Flow

### For Admins
1. After confirming an order, create a rider assignment document in Firestore with:
   - `status: 'assigned'`
   - `riderId`: UID of the assigned rider
   - `orderId`: ID of the order
   - `assignedAt`: Server timestamp
   - `orderOwnerUserId`: UID of the order creator

### For Riders
1. Login with a user account that has `role: 'rider'` in Firestore
2. See dashboard with assigned deliveries
3. **Accept/Decline**: Choose to accept or provide decline reason
4. **Track Status**:
   - Accepted → Mark as Picked Up
   - Picked Up → Mark as In Transit
   - In Transit → Mark as Delivered
5. **View History**: Completed tab shows all delivered orders and cumulative earnings

## Setup Instructions

### 1. Deploy Firestore Rules
```bash
firebase deploy --only firestore:rules
```
OR manually upload the rules from `firestore.rules` to Firebase Console.

### 2. Create Test Rider Account (via Firebase Console)
1. Go to Firebase Console → Authentication
2. Create new user (e.g., rider@test.com)
3. Go to Firestore → users collection
4. Create/update document with UID:
   ```json
   {
     "email": "rider@test.com",
     "displayName": "John Rider",
     "role": "rider",
     "isAdmin": false,
     "isBanned": false,
     "createdAt": Timestamp.now()
   }
   ```

### 3. Assign Orders to Riders (via Firestore Console or Admin Panel)
1. Create document in `riderAssignments` collection:
   ```json
   {
     "orderId": "...",
     "riderId": "...",
     "orderOwnerUserId": "...",
     "status": "assigned",
     "assignedAt": Timestamp.now(),
     "earnings": 10.00
   }
   ```

### 4. Test the Flow
1. Login as admin, confirm an order
2. Login as rider, accept delivery
3. Update status through stages
4. Verify earnings calculation in completed tab

## Integration with Order Management

### How Orders and Riders Connect
1. Admin confirms order → status becomes 'shipped'
2. Admin/System creates riderAssignment with orderId and status 'assigned'
3. Rider accepts assignment → status becomes 'accepted'
4. Rider marks as picked up → status becomes 'pickedUp'
5. Rider marks as in transit → status becomes 'inTransit'
6. Rider marks as delivered → status becomes 'delivered', order owner notified
7. Buyer can then confirm delivery in their account

### Order Status vs Rider Status
- **Order Collection**: Tracks order lifecycle from buyer perspective (pending → shipped → delivered → completed)
- **RiderAssignment**: Tracks delivery execution from rider perspective (assigned → accepted → pickedUp → inTransit → delivered)

## Future Enhancements

1. **GPS Tracking**: Add location tracking during delivery
2. **Notifications**: Real-time push notifications for new assignments
3. **Rating System**: Buyers rate riders, riders track ratings
4. **Batch Assignments**: Assign multiple orders to a rider
5. **Earnings Report**: Detailed breakdown of earnings by order/date
6. **Performance Metrics**: Delivery time, success rate, rating average
7. **Admin Dashboard**: View all riders, their earnings, active deliveries, completion rate
8. **Withdrawal System**: Riders withdraw earnings to bank accounts

## Troubleshooting

### Rider Dashboard Shows "No Authenticated User"
- Ensure user is logged in and has `role: 'rider'` in Firestore users collection
- Check Firebase Auth UID matches the riderId in assignments

### Can't See Assigned Deliveries
- Verify Firestore rules are deployed (check Firebase Console)
- Check `riderId` field in riderAssignments matches current user's UID
- Check `status` is 'assigned'

### Permission Denied on Updates
- Verify rider's UID matches `riderId` in the assignment
- Ensure only allowed fields are being updated (status, timestamps, notes, earnings)
- Check Firestore rules for syntax errors

## Files Modified/Created

**Created:**
- `lib/models/rider_assignment.dart` - Rider assignment data model
- `lib/providers/rider_provider.dart` - State management for rider operations
- `lib/screens/rider/rider_dashboard_screen.dart` - Main UI for riders
- `RIDER_DASHBOARD_SETUP.md` - This file

**Modified:**
- `lib/models/user.dart` - Added role field
- `lib/providers/auth_provider.dart` - Load and store user role
- `lib/config/routes.dart` - Added rider route
- `lib/main.dart` - Added RiderProvider and role-based routing
- `firestore.rules` - Added riderAssignments rules

